#!/usr/bin/env python3
"""Local execution of notebooks/day2_annotation_to_yolo.ipynb (Colab-adapted)."""
from __future__ import annotations
import json, math, os, shutil, subprocess, sys
from pathlib import Path

os.environ.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
os.environ.setdefault("MPLBACKEND", "Agg")

import torch
import yaml
from ultralytics import YOLO

ROOT = Path(__file__).resolve().parent if False else Path.cwd()
# When launched from repo root:
ROOT = Path.cwd().resolve()
assert (ROOT / "notebooks/day2_annotation_to_yolo.ipynb").is_file(), ROOT
assert (ROOT / "dataset/labels/train").is_dir()

# Notebook cell 2 adaptations for local Mac:
# - LAB_ROOT = current repo (already pushed); skip clone
# - DEVICE = mps when available (notebook only checks CUDA)
# - batch = 4 (AutoBatch=-1 is flaky on MPS/16GB)
LAB_ROOT = ROOT
DATA_YAML = LAB_ROOT / "data.yaml"
TRAIN_IMAGES = LAB_ROOT / "dataset/images/train"
TRAIN_LABELS = LAB_ROOT / "dataset/labels/train"
EVAL_IMAGES = LAB_ROOT / "dataset/images/eval"
EVAL_LABELS = LAB_ROOT / "dataset/labels/eval"
RUNS = LAB_ROOT / "outputs/yolo26_runs"
DEVICE = "mps" if torch.backends.mps.is_available() else ("0" if torch.cuda.is_available() else "cpu")
BATCH = 4

last_commit = subprocess.run(
    ["git", "-C", str(LAB_ROOT), "log", "-1", "--oneline"],
    check=True, capture_output=True, text=True,
).stdout.strip()
print("commit:", last_commit, flush=True)

_data_cfg = yaml.safe_load(DATA_YAML.read_text(encoding="utf-8"))
# Do NOT rewrite data.yaml in-place (dirty git). Use a local copy like train_yolo_local.
local_yaml = LAB_ROOT / "outputs/data_notebook_local.yaml"
_data_cfg["path"] = str((LAB_ROOT / "dataset").resolve())
local_yaml.parent.mkdir(parents=True, exist_ok=True)
local_yaml.write_text(yaml.dump(_data_cfg, allow_unicode=True, sort_keys=False), encoding="utf-8")
print("LAB_ROOT:", LAB_ROOT)
print("device:", DEVICE, "batch:", BATCH)

# Cell 3
def image_stems(directory):
    return {p.stem for ext in ("*.jpg", "*.jpeg", "*.png") for p in directory.glob(ext)}

train_images = image_stems(TRAIN_IMAGES)
train_labels = {p.stem for p in TRAIN_LABELS.glob("*.txt")}
eval_images = image_stems(EVAL_IMAGES)
eval_labels = {p.stem for p in EVAL_LABELS.glob("*.txt")}
assert len(train_images) == 50, f"can 50 train images, thay {len(train_images)}"
assert train_images == train_labels, f"train images/labels lech: {sorted(train_images ^ train_labels)[:5]}"
assert len(eval_images) == 10 and eval_images == eval_labels, "eval phai du 10 anh va nhan"
print(f"OK: {len(train_images)} train + {len(eval_images)} eval", flush=True)

# Cell 5
model = YOLO("yolo26n.pt")
train_result = model.train(
    data=str(local_yaml),
    epochs=50,
    imgsz=640,
    batch=BATCH,
    device=DEVICE,
    workers=0,
    project=str(RUNS),
    name="vehicle_annotation",
    exist_ok=True,
    seed=20260909,
    plots=True,
    amp=False,
)
BEST = Path(model.trainer.best)
print("best checkpoint:", BEST, flush=True)

# Cell 7
best_model = YOLO(str(BEST))
metrics = best_model.val(
    data=str(local_yaml), split="val", device=DEVICE, plots=True,
    project=str(RUNS), name="vehicle_eval", exist_ok=True, workers=0, batch=BATCH, amp=False,
)
summary = {
    "precision": float(metrics.box.mp),
    "recall": float(metrics.box.mr),
    "map50": float(metrics.box.map50),
    "map50_95": float(metrics.box.map),
    "eval_images": len(eval_images),
    "checkpoint": str(BEST),
    "device": DEVICE,
    "batch": BATCH,
    "source": "notebooks/day2_annotation_to_yolo.ipynb (local adapted)",
}
metrics_path = LAB_ROOT / "outputs/model_eval_metrics.json"
metrics_path.write_text(json.dumps(summary, indent=2) + "\n")
print(json.dumps(summary, indent=2), flush=True)

# Cell 8
prediction_dir = LAB_ROOT / "outputs/eval_predictions"
results = best_model.predict(
    source=str(EVAL_IMAGES), conf=0.25, device=DEVICE, save=True,
    project=str(prediction_dir), name="visuals", exist_ok=True,
)
PRED_SAVE_DIR = Path(results[0].save_dir)
print("predictions saved to:", PRED_SAVE_DIR, flush=True)

# Build zip like notebook, but exclude large .pt weights to keep zip small/safe
staging = LAB_ROOT / "outputs/_day2_zip_staging"
if staging.exists():
    shutil.rmtree(staging)
staging.mkdir(parents=True)
for name in ("eval_predictions", "yolo26_runs"):
    src = LAB_ROOT / "outputs" / name
    if src.exists():
        shutil.copytree(src, staging / name, ignore=shutil.ignore_patterns("*.pt", "weights", "*.cache"))
shutil.copy2(metrics_path, staging / "model_eval_metrics.json")
archive = shutil.make_archive(str(LAB_ROOT / "outputs/day2_colab_outputs"), "zip", staging)
shutil.rmtree(staging)
print("Da tao:", archive, flush=True)

# Cell 10 (save figure instead of show)
import matplotlib.pyplot as plt
from PIL import Image
pred_images = sorted(PRED_SAVE_DIR.glob("*.jpg"))
cols = 5
rows = math.ceil(len(pred_images) / cols) if pred_images else 1
fig, axes = plt.subplots(rows, cols, figsize=(4 * cols, 4 * rows))
axes = axes.flat if hasattr(axes, "flat") else [axes]
for ax, img_path in zip(axes, pred_images):
    ax.imshow(Image.open(img_path))
    ax.set_title(img_path.name, fontsize=9)
    ax.axis("off")
for ax in list(axes)[len(pred_images):]:
    ax.axis("off")
plt.tight_layout()
overview = LAB_ROOT / "outputs/eval_predictions/eval_overview.jpg"
overview.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(overview, dpi=120)
plt.close(fig)
print("overview:", overview, flush=True)
print("NOTEBOOK_LOCAL_COMPLETE", flush=True)
