# Hướng dẫn thực hành Ngày 2

**Bài cá nhân.** Mỗi học viên tự làm và nộp bộ nhãn của mình. Hạn nộp: **11:59 trưa ngày hôm sau buổi lab (giờ Việt Nam, UTC+7)**. Với buổi ngày 09/11/2026, hạn nộp là **11:59 ngày 10/11/2026**. Kênh nộp theo thông báo của giảng viên.

Nộp link repo trên LMS bằng tài khoản cá nhân. Tên repo/file và checklist nộp bài xem [SUBMISSION.md](SUBMISSION.md); điền [báo cáo cá nhân](report/individual/2A202603275_HoangMinhHai.md) từ kết quả thực tế. Quy định làm bài ở [RULES.md](RULES.md), sản phẩm từng bước ở [CHECKPOINTS.md](CHECKPOINTS.md).

## 0. Phân bổ thời gian (4 giờ)

| Thời lượng | Hoạt động | Kết quả phải có |
| ---: | --- | --- |
| 0:00-0:25 | Đọc schema, xem ảnh, thống nhất quy tắc | ghi ba ca mơ hồ vào `GUIDELINE_MINI.md` |
| 0:25-2:15 | Gán nhãn 50 ảnh train | 50 file YOLO trong `dataset/labels/train/` |
| 2:15-2:40 | Self-QC và kiểm tra cấu trúc | `check_yolo_labels.py` chạy đạt |
| 2:40-3:00 | Nộp/khóa nhãn, nhận gold labels từ giảng viên | không sửa nhãn trước khi chạy đánh giá |
| 3:00-3:20 | Chấm nhãn với gold set, rework nếu cần | F1 >= 0.80 và mean IoU >= 0.70 |
| 3:20-4:00 | Mở notebook Colab (tự clone repo của bạn), train và evaluate YOLO | link Colab, ảnh/chỉ số eval |

## 1. Quy tắc gán nhãn

### Quy tắc vẽ box

- Mỗi xe hợp lệ là **một box riêng**; năm xe có năm box, kể cả cùng lớp.
- Box ôm sát phần thân xe nhìn thấy được, không lấy thêm mặt đường, trời hay xe bên cạnh.
- Box chạm đúng rìa ảnh khi vật thể bị cắt khung; không đoán phần nằm ngoài ảnh.
- Vật thể bị che một phần vẫn gán box quanh phần nhìn thấy được nếu nhận diện được lớp.
- Nếu chỉ còn mảnh rất nhỏ, không thể xác định chắc lớp, **không tự đoán**. Ghi vào mini guideline và hỏi giảng viên.
- Không gán người đi bộ, xe đạp, mô tô/xe máy, biển báo, đèn giao thông hoặc vật thể ngoài bốn lớp của schema.

### Các quyết định cần nhất quán

| Tình huống | Quyết định |
| --- | --- |
| Xe đang đỗ | vẫn gán lớp theo loại xe |
| Hai xe chồng lên nhau | vẽ hai box riêng trên phần nhìn thấy của từng xe |
| Mô tô/xe máy trong cảnh | không gán; không thuộc bốn lớp của schema |
| Van/minivan mơ hồ với `bus` hoặc `car` | không tự chọn; ghi case ID và hỏi |
| Phản chiếu trong kính/gương | không gán nếu không phải xe thật trong cảnh |
| Bảng quảng cáo có hình xe | không gán |

## 2. Tạo nhãn YOLO

Bạn có thể dùng CVAT, Label Studio, Roboflow Annotate hoặc bất cứ công cụ nào export được YOLO detection. Khi export, kiểm tra tên file phải như sau:

```text
dataset/images/train/drive_001.jpg
dataset/labels/train/drive_001.txt
```

Mỗi dòng nhãn có đúng năm số:

```text
<class_id> <x_center> <y_center> <width> <height>
0 0.482000 0.613500 0.153100 0.213900
```

Tọa độ được chuẩn hóa trong khoảng `[0, 1]`; `width` và `height` phải lớn hơn 0, box không được vượt biên ảnh. Một ảnh không có xe thuộc schema vẫn phải có file `.txt` rỗng. Không thêm confidence, tên lớp, pixel coordinate hoặc cột thứ sáu.

### Nếu công cụ xuất tọa độ pixel

Với ảnh rộng `W`, cao `H` và box pixel `(x_min, y_min, x_max, y_max)`:

```text
x_center = ((x_min + x_max) / 2) / W
y_center = ((y_min + y_max) / 2) / H
width    = (x_max - x_min) / W
height   = (y_max - y_min) / H
```

## 3. Self-QC trước khi nộp

Chạy từ thư mục gốc repo (bản clone fork của bạn):

```bash
python3 tools/check_yolo_labels.py
```

Lệnh này kiểm tra đủ 50 file, đúng basename, năm cột, ID lớp và box không vượt biên. Lệnh đạt **không chứng minh** box đã đúng; bạn vẫn phải mở ngẫu nhiên ít nhất 10 ảnh và kiểm tra completeness, tightness, class.

Checklist trước khi khóa nhãn:

- [ ] Có đúng 50 file `.txt` trong `dataset/labels/train/`.
- [ ] Mỗi xe thuộc schema đã có một box; không bỏ sót xe bị che/cắt khung có thể nhận diện.
- [ ] Không có box lỏng hoặc gộp hai xe thành một box.
- [ ] Không nhầm `truck`, `bus`, `car`, `van`.
- [ ] `GUIDELINE_MINI.md` nêu định nghĩa lớp và ít nhất ba quyết định mơ hồ.

## 4. Chấm nhãn với ground truth

Giảng viên phát thư mục nhãn chuẩn (ground truth) `gold_train_labels/` sau khi cả lớp nộp/khóa nhãn. Chép thư mục này cùng cấp với `dataset/`, rồi chạy:

```bash
python3 tools/evaluate_annotations.py \
  --student-labels dataset/labels/train \
  --gold-labels gold_train_labels \
  --output outputs/annotation_evaluation.json
```

Chương trình ghép box **cùng lớp** tại IoU >= 0.50; mỗi box chỉ được ghép với một box phía còn lại:

- `precision = TP / (TP + FP)`: box bạn vẽ, bao nhiêu box đúng?
- `recall = TP / (TP + FN)`: xe trong gold set, bạn bắt được bao nhiêu?
- `F1`: cân bằng precision và recall.
- `mean_iou_of_matches`: IoU trung bình của các box đã ghép.

Bạn hoàn thành bước kiểm tra annotation khi `F1 >= 0.80` và `mean_iou_of_matches >= 0.70`. Nếu chưa đạt, mở lại ảnh để kiểm tra: `FN` có thể do bỏ sót, sai lớp hoặc box lệch; `FP` có thể do box thừa, sai lớp hoặc không khớp vị trí. Với IoU thấp, kiểm tra lại các cạnh box. Sửa nhãn rồi chạy lại.

## 5. Train và đánh giá model trên Google Colab

Chỉ train sau khi đạt cả hai ngưỡng kiểm tra annotation. Mở `notebooks/day2_annotation_to_yolo.ipynb` trong Colab từ repo của bạn, dán URL repo vào `REPO_URL` — notebook tự clone repo đã push, không cần upload file. Không upload hay commit `gold_train_labels/`. Notebook sẽ:

1. cài Ultralytics phiên bản mới nhất;
2. clone repo của bạn (từ `REPO_URL`) và xác nhận 50 nhãn train và 10 nhãn eval;
3. train `yolo26n.pt` với `data.yaml`;
4. evaluate `best.pt` trên **10 ảnh eval** có nhãn;
5. lưu `results.csv`, confusion matrix, ảnh prediction và metrics;
6. hiển thị cả 10 ảnh eval kèm box dự đoán ngay trong notebook để kiểm tra nhanh.

Không đưa `dataset/images/eval/` hoặc `dataset/labels/eval/` vào train. Kết quả model thấp trên tập chỉ 50 ảnh không phải lý do sửa gold labels; hãy phân tích nó như tín hiệu về độ phủ dữ liệu, class imbalance và chất lượng annotation.

Lưu ý: `truck`/`bus`/`van` xuất hiện ít hơn `car` nhiều trong tập train. Nếu model chủ yếu nhận diện được `car`, hãy kiểm tra cả sự mất cân bằng số lượng giữa các lớp (class imbalance) và chất lượng annotation trước khi kết luận nguyên nhân.

Trong notebook này, 10 ảnh `eval` cũng được dùng làm validation trong quá trình train và chọn `best.pt`. Đây không phải test set độc lập. Giữ nguyên split và không dùng `eval` để train.
