# Bài thực hành Ngày 2 - Gán nhãn phát hiện vật thể cho ADAS

> **Trạng thái bài làm cá nhân (09/11/2026):** xem [báo cáo của Hoàng Minh Hải](report/individual/2A202603275_HoangMinhHai.md). Annotation QC sau rework: F1 0,8469, mean IoU 0,8265. **Đã train YOLO26n local trong PyCharm 50 epoch**, mAP50 0.6550, mAP50–95 0.4089; có đủ 10 ảnh prediction. Đã rework để đồng bộ ID lớp giữa CVAT, `data.yaml` và gold sau khi phát hiện thứ tự lớp khác schema ban đầu; chi tiết các lượt QC box nằm trong báo cáo. Hình thức local thay Colab cần được giảng viên xác nhận.

**Bài cá nhân.** Mỗi học viên tự làm và nộp bộ nhãn của mình. Hạn nộp: **11:59 trưa ngày hôm sau buổi lab (giờ Việt Nam, UTC+7)**. Với buổi ngày 09/11/2026, hạn nộp là **11:59 ngày 10/11/2026**. Nộp bài qua LMS tại [aithucchien.vinuni.edu.vn](https://aithucchien.vinuni.edu.vn).

Repo đề bài: `K5-L2-Day02-ObjectDetection`, dùng chung cho K5 Level 2. Mỗi học viên tự nộp link repo bài làm trên [LMS AI Thực chiến](https://aithucchien.vinuni.edu.vn) bằng tài khoản cá nhân; tên repo và các file cần nộp ở [SUBMISSION.md](SUBMISSION.md).

Trong bốn giờ, bạn sẽ tạo nhãn chuẩn (ground truth) cho ảnh cảnh giao thông, kiểm tra chất lượng nhãn bằng gold set do giảng viên cung cấp, sau đó train và đánh giá YOLO. Bài thực hành mô phỏng phần dữ liệu của hệ thống hỗ trợ người lái (ADAS):

```text
camera -> annotation guideline -> nhãn YOLO -> QC với gold set -> train detector -> đánh giá trên eval set
```

Mục tiêu chính là nhãn đúng và nhất quán. Kết quả mô hình giúp bạn kiểm tra ảnh hưởng của dữ liệu và chất lượng nhãn.

## Mục tiêu học tập

Sau lab, bạn có thể:

1. Thiết kế và áp dụng schema bốn lớp cho cảnh giao thông.
2. Vẽ bounding box 2D bám sát vật thể, đầy đủ và nhất quán cho vật thể bị che khuất hoặc cắt khung.
3. Xuất/kiểm tra nhãn YOLO: một file `.txt` cho một ảnh, cùng basename với ảnh.
4. Dùng Precision, Recall, F1 và IoU để kiểm tra **nhãn con người** với gold set.
5. Train từ checkpoint YOLO theo notebook trong Google Colab và đánh giá model trên eval set.

## Thứ tự đọc tài liệu

Đọc các file `.md` theo thứ tự trước khi bắt tay vào lab. Mỗi file giữ một vai trò; không bỏ qua `RULES.md` và `CHECKPOINTS.md` vì chúng đặt khung giới hạn và mốc phải có.

| # | File | Nội dung | Khi đọc |
| ---: | --- | --- | --- |
| 1 | [RULES.md](RULES.md) | Quy định làm bài, hợp tác, gold/split, secret | Đọc đầu tiên, trước mọi thứ |
| 2 | [CHECKPOINTS.md](CHECKPOINTS.md) | Sản phẩm từng bước + thời lượng 4 giờ | Đọc để nắm mốc và thứ tự thao tác |
| 3 | [GUIDE.md](GUIDE.md) | Cách làm chi tiết từng bước (nhãn, QC, gold, train/eval) | Đọc và làm theo trong suốt buổi lab |
| 4 | [GUIDELINE_MINI.md](GUIDELINE_MINI.md) | Mẫu guideline cá nhân **bạn phải điền** | Điền **trước** khi gán nhãn (CP1) |
| 5 | [RUBRIC.md](RUBRIC.md) | Tiêu chí chấm điểm và mức chất lượng | Đọc trước khi làm để biết cần đạt gì |
| 6 | [SUBMISSION.md](SUBMISSION.md) | Cách đặt tên repo, cấu trúc nộp, xử lý kết quả Colab | Đối chiếu **trước khi nộp** |
| 7 | [report/individual/2A202603275_HoangMinhHai.md](report/individual/2A202603275_HoangMinhHai.md) | Mẫu báo cáo cá nhân | Điền **cuối cùng**, tập hợp kết quả |

> Mẹo: đọc 1–3 và 5 trước buổi lab để nắm rõ ràng phải làm và chấm; điền 4 (guideline) trong buổi; đối chiếu 6 và điền 7 ở giai đoạn nộp.

## Bài nộp

- `dataset/labels/train/`: 50 file nhãn YOLO, mỗi file ứng với một ảnh trong `dataset/images/train/`.
- `GUIDELINE_MINI.md`: định nghĩa lớp và quyết định cho ít nhất ba ca mơ hồ quan sát được.
- `outputs/annotation_evaluation.json`: kết quả chấm sau khi giảng viên phát gold labels.
- Link Colab đã chạy và ảnh/chỉ số đánh giá model trên tập `eval`.

Điền [báo cáo cá nhân](report/individual/2A202603275_HoangMinhHai.md) để tập hợp các đầu ra trên; mẫu báo cáo không thêm bài tập hoặc tiêu chí điểm mới.

## Chuẩn bị và bắt đầu

- Có tài khoản GitHub để lưu bài, công cụ annotation xuất được YOLO detection (CVAT, Label Studio hoặc Roboflow Annotate) và Google Colab để chạy notebook.
- Có Python 3 trên máy để chạy hai script trong `tools/`; hai script này chỉ dùng thư viện chuẩn Python. Dùng `python3` hoặc `python` tùy cách cài Python, nhưng chạy lệnh từ thư mục gốc bài lab.
- **Fork repo đề bài** về tài khoản GitHub cá nhân (đặt tên theo chuẩn nộp ở [SUBMISSION.md](SUBMISSION.md)). Không lấy repo giảng viên hoặc gold train làm dữ liệu annotation.
- Gán nhãn rồi **commit và push** `dataset/labels/train/` lên repo của bạn — đây là bản dữ liệu Colab sẽ tự clone.
- Trên Colab, mở notebook `notebooks/day2_annotation_to_yolo.ipynb` (từ trang GitHub của repo, mở bằng nút Colab, hoặc dán URL repo). Chọn runtime có GPU nếu được cấp. Cell đầu tự clone repo của bạn về Colab — không cần upload file hay zip.

Đọc các file tài liệu theo thứ tự ở mục **Thứ tự đọc tài liệu** ở trên; khi chuẩn bị nộp, đối chiếu [SUBMISSION.md](SUBMISSION.md), [RUBRIC.md](RUBRIC.md) và [mẫu báo cáo](report/individual/2A202603275_HoangMinhHai.md).

## Cấu trúc thư mục

```text
Day2-Lab/
  dataset/
    images/train/       # 50 ảnh: sinh viên gán nhãn
    images/eval/        # 10 ảnh: dùng làm validation và đánh giá model
    labels/train/       # để trống khi pull; sinh viên tạo nhãn ở đây
    labels/eval/        # gold labels cho validation và đánh giá model
  notebooks/
    day2_annotation_to_yolo.ipynb
  tools/
    check_yolo_labels.py
    evaluate_annotations.py
  data.yaml
```

Không đổi tên ảnh, không đổi thứ tự ID lớp và không dùng `eval` để train. Nhãn gold của 50 ảnh train không có trong repository sinh viên; giảng viên chỉ phát sau khi khóa nộp nhãn.

## Schema bắt buộc

| ID | Lớp | Gán khi | Không gán khi |
| ---: | --- | --- | --- |
| 0 | `car` | xe con, sedan, SUV, taxi, xe bán tải | xe buýt, xe tải, mô tô |
| 1 | `truck` | xe tải chở hàng, xe đầu kéo | xe bán tải/cabin nhỏ thuộc `car` |
| 2 | `bus` | xe buýt, minibus chở khách | van chở hàng/chở người thuộc `van` |
| 3 | `van` | xe van, minivan chở hàng hoặc chở người | xe buýt lớn (`bus`) hoặc xe con thông thường (`car`) |

Các lớp này mô tả **loại vật thể**, không mô tả trạng thái. Xe đang đỗ vẫn là `car`; bị che một phần vẫn cần box nếu phần nhìn thấy đủ để nhận diện lớp.

## Điều kiện đi tiếp

Sau khi giảng viên phát `gold_train_labels/`, chạy:

```bash
python3 tools/evaluate_annotations.py \
  --student-labels dataset/labels/train \
  --gold-labels gold_train_labels
```

Điều kiện hoàn thành annotation là `F1 >= 0.80` tại IoU 0.50 **và** `mean_iou_of_matches >= 0.70`. Chưa đạt thì sửa nhãn trước khi train. Đây là chỉ số annotation, không phải mAP của model.

## Ghi chú dữ liệu

Bộ ảnh là một tập con ảnh cảnh giao thông CCTV (nguồn gốc UA-DETRAC, phát hành lại dưới giấy phép CC-BY-4.0) đã được biên tập cho mục đích giảng dạy. Ảnh được đổi tên tuần tự và re-encode để loại bỏ metadata; repository không chứa ID ảnh nguồn, URL, hay nhãn train gold. Không đảo ngược, truy vết hay dùng thông tin ngoài repo để tìm nhãn.

Chỉ dùng ảnh và nhãn trong phạm vi bài học. Không bổ sung ảnh cá nhân, biển số, dữ liệu khách hàng hoặc dữ liệu nhạy cảm vào repository/Colab công khai.

## Chạy YOLO local trong PyCharm

Dùng interpreter `.venv` của dự án, mở `tools/train_yolo_local.py` và bấm Run, hoặc chạy:

```bash
./.venv/bin/python tools/train_yolo_local.py --device mps --epochs 50 --batch 4
```

Script dùng 50 ảnh train và 10 ảnh eval riêng, lưu best checkpoint trong `outputs/yolo26_runs/`, đánh giá lại và tạo prediction cùng assets báo cáo. Kết quả model nằm trong `outputs/model_eval_metrics.json`; F1 annotation vẫn nằm riêng ở `outputs/annotation_evaluation.json`. Pretrained checkpoint được tải từ nguồn Ultralytics khi chưa có trên máy.
