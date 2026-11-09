#!/usr/bin/env python3
"""Train/evaluate the Day02 lab locally; runnable directly in PyCharm."""
from __future__ import annotations

import argparse
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time
import traceback

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("MPLBACKEND", "Agg")

ROOT = Path(__file__).resolve().parents[1]
OUTPUTS = ROOT / "outputs"
STATUS = OUTPUTS / "local_training_status.json"


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n")
    temporary.replace(path)


class Tee(io.TextIOBase):
    def __init__(self, terminal, log):
        self.terminal, self.log = terminal, log

    def write(self, value):
        self.terminal.write(value)
        self.log.write(value)
        self.flush()
        return len(value)

    def flush(self):
        self.terminal.flush()
        self.log.flush()

    def isatty(self):
        return False


def main(args) -> None:
    import torch
    import ultralytics
    import yaml
    from ultralytics import YOLO

    started = time.time()
    state = {
        "state": "checking",
        "pid": os.getpid(),
        "started_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "epochs_requested": args.epochs,
    }

    def status(phase, **details):
        state.update(state=phase, **details)
        write_json(STATUS, state)

    try:
        os.chdir(ROOT)
        config = yaml.safe_load((ROOT / "data.yaml").read_text())
        expected = {0: "car", 1: "van", 2: "truck", 3: "bus"}
        assert config["names"] == expected, "data.yaml class schema does not match the reviewed labels"
        train_images = sorted((ROOT / "dataset/images/train").glob("*.jpg"))
        eval_images = sorted((ROOT / "dataset/images/eval").glob("*.jpg"))
        assert len(train_images) == 50 and len(eval_images) == 10
        for split, images in [("train", train_images), ("eval", eval_images)]:
            labels = sorted((ROOT / f"dataset/labels/{split}").glob("*.txt"))
            assert {p.stem for p in images} == {p.stem for p in labels}, split
        assert not ({p.stem for p in train_images} & {p.stem for p in eval_images})
        assert not ({hashlib.sha256(p.read_bytes()).hexdigest() for p in train_images}
                    & {hashlib.sha256(p.read_bytes()).hexdigest() for p in eval_images})
        subprocess.run([sys.executable, str(ROOT / "tools/check_yolo_labels.py")], check=True)
        qc = json.loads((OUTPUTS / "annotation_evaluation.json").read_text())
        assert qc["passed"] and qc["f1"] >= 0.8 and qc["mean_iou_of_matches"] >= 0.7

        device = args.device
        if device == "auto":
            device = "mps" if torch.backends.mps.is_available() else ("0" if torch.cuda.is_available() else "cpu")
        if device == "mps":
            assert torch.backends.mps.is_available(), "MPS is unavailable in this process"
        torch.set_num_threads(4)
        config["path"] = str(ROOT / "dataset")
        local_config = OUTPUTS / "data_local.yaml"
        local_config.write_text(yaml.safe_dump(config, allow_unicode=True, sort_keys=False))
        manifest = {
            "python": platform.python_version(), "torch": torch.__version__,
            "ultralytics": ultralytics.__version__, "device": device,
            "epochs": args.epochs, "batch": args.batch, "imgsz": 640,
            "seed": 20260909, "workers": 0, "model": "yolo26n.pt",
            "train_images": 50, "eval_images": 10, "annotation_f1": qc["f1"],
            "label_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for split in ["train", "eval"]
                             for p in sorted((ROOT / f"dataset/labels/{split}").glob("*.txt"))},
            "image_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                             for p in train_images + eval_images},
        }
        write_json(OUTPUTS / "local_run_manifest.json", manifest)
        print(f"READY: 50 train / 10 eval; device={device}; epochs={args.epochs}; batch={args.batch}", flush=True)
        status("loading_pretrained", device=device, batch=args.batch, manifest=str(OUTPUTS / "local_run_manifest.json"))
        model = YOLO("yolo26n.pt")

        def epoch_done(trainer):
            status("training", epoch=min(trainer.epoch + 1, args.epochs), train_dir=str(trainer.save_dir),
                   elapsed_seconds=round(time.time() - started, 1))

        model.add_callback("on_fit_epoch_end", epoch_done)
        status("training", epoch=0)
        model.train(data=str(local_config), epochs=args.epochs, imgsz=640,
                    batch=args.batch, device=device, workers=0,
                    project=str(OUTPUTS / "yolo26_runs"), name="vehicle_annotation",
                    exist_ok=False, seed=20260909, plots=True, cache=False,
                    save=True, amp=False)
        best = Path(model.trainer.best)
        train_dir = Path(model.trainer.save_dir)
        assert best.is_file(), best
        status("evaluating", checkpoint=str(best), train_dir=str(train_dir))
        best_model = YOLO(str(best))
        validation_output = {}
        best_model.add_callback("on_val_start", lambda validator: validation_output.update(path=Path(validator.save_dir)))
        metrics = best_model.val(data=str(local_config), split="val", imgsz=640,
                                 batch=args.batch, device=device, workers=0,
                                 plots=True, project=str(OUTPUTS / "yolo26_runs"),
                                 name="vehicle_eval", exist_ok=False)
        eval_dir = validation_output["path"]
        per_class = []
        for k, class_id in enumerate(metrics.box.ap_class_index):
            class_id = int(class_id)
            per_class.append({"class_id": class_id, "name": best_model.names[class_id],
                              "precision": float(metrics.box.p[k]), "recall": float(metrics.box.r[k]),
                              "map50": float(metrics.box.ap50[k]), "map50_95": float(metrics.box.ap[k])})
        summary = {"precision": float(metrics.box.mp), "recall": float(metrics.box.mr),
                   "map50": float(metrics.box.map50), "map50_95": float(metrics.box.map),
                   "eval_images": 10, "checkpoint": str(best), "train_dir": str(train_dir),
                   "eval_dir": str(eval_dir), "per_class": per_class,
                   "runtime": manifest, "training_seconds": round(time.time() - started, 1)}
        write_json(OUTPUTS / "model_eval_metrics.json", summary)
        print("MODEL_METRICS", json.dumps(summary, ensure_ascii=False), flush=True)
        status("predicting", eval_dir=str(eval_dir))
        predictions = best_model.predict(source=str(ROOT / "dataset/images/eval"),
                                          conf=0.25, imgsz=640, device=device, batch=1,
                                          save=True, save_txt=True, save_conf=True,
                                          project=str(OUTPUTS / "eval_predictions"),
                                          name="visuals", exist_ok=False)
        assert len(predictions) == 10
        prediction_dir = Path(predictions[0].save_dir)
        assert all((prediction_dir / p.name).is_file() for p in eval_images)
        summary["prediction_dir"] = str(prediction_dir)
        summary["total_seconds"] = round(time.time() - started, 1)
        write_json(OUTPUTS / "model_eval_metrics.json", summary)

        # Preserve predictions in a machine-readable form for later visual error analysis.
        write_json(OUTPUTS / "eval_predictions_at_conf025.json", {"conf": 0.25, "images": [
            {"image": Path(result.path).name, "classes": result.boxes.cls.cpu().tolist(),
             "confidences": result.boxes.conf.cpu().tolist(), "xywhn": result.boxes.xywhn.cpu().tolist()}
            for result in predictions]})
        assets = ROOT / "report/individual/assets"
        shutil.copytree(train_dir, assets / "yolo26_runs/vehicle_annotation", dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("weights", "*.pt", "*.cache"))
        shutil.copytree(eval_dir, assets / "yolo26_runs/vehicle_eval", dirs_exist_ok=True,
                        ignore=shutil.ignore_patterns("weights", "*.pt", "*.cache"))
        shutil.copytree(prediction_dir, assets / "eval_predictions/visuals", dirs_exist_ok=True)
        shutil.copy2(OUTPUTS / "model_eval_metrics.json", assets / "model_eval_metrics.json")
        shutil.copy2(OUTPUTS / "local_run_manifest.json", assets / "local_run_manifest.json")
        status("complete", epoch=args.epochs, checkpoint=str(best), train_dir=str(train_dir), eval_dir=str(eval_dir),
               prediction_dir=str(prediction_dir), metrics=str(OUTPUTS / "model_eval_metrics.json"),
               total_seconds=round(time.time() - started, 1))
        print("COMPLETE: training, validation, 10 predictions, and submission assets saved.", flush=True)
    except BaseException as exc:
        status("failed", error=f"{type(exc).__name__}: {exc}", elapsed_seconds=round(time.time() - started, 1))
        traceback.print_exc()
        raise


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--epochs", type=int, default=50)
    parser.add_argument("--batch", type=int, default=4)
    parser.add_argument("--device", default="auto")
    args = parser.parse_args()
    OUTPUTS.mkdir(exist_ok=True)
    with (OUTPUTS / "local_training_console.log").open("a", buffering=1) as log:
        with contextlib.redirect_stdout(Tee(sys.stdout, log)), contextlib.redirect_stderr(Tee(sys.stderr, log)):
            main(args)
