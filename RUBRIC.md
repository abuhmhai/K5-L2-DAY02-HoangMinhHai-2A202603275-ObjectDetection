# Tiêu chí đánh giá Ngày 2 — Object Detection Annotation (100 điểm)

Bài cá nhân, tổng điểm chính 100; bài này không có hạng mục bonus riêng. Cách đặt tên/nộp bài và deadline ở [SUBMISSION.md](SUBMISSION.md), quy định làm bài ở [RULES.md](RULES.md). [Báo cáo cá nhân](report/individual/2A202603275_HoangMinhHai.md) tập hợp kết quả của các tiêu chí dưới đây, không có điểm cộng riêng cho độ dài báo cáo.

| Tiêu chí | Kết quả bài làm | Điểm |
| --- | --- | ---: |
| Hoàn thành và định dạng YOLO | 50 file cùng basename, 5 cột, normalized, bốn class ID đúng | 10 |
| Đầy đủ vật thể | gán đủ xe thuộc schema, kể cả xe che/cắt khung có thể nhận diện | 20 |
| Độ bám sát và hình học box | box sát phần vật thể nhìn thấy, không lấn nền/gộp vật thể | 20 |
| Phân lớp nhất quán | phân biệt `car/truck/bus/van`, không gán vật thể ngoài scope | 15 |
| Mini guideline và quyết định mơ hồ | định nghĩa lớp, quy tắc box, ít nhất ba case có lý do | 10 |
| Gold-set annotation QC | `F1 >= 0.80` và `mean IoU >= 0.70` hoặc có vòng rework được giải thích rõ | 15 |
| Pipeline YOLO và phân tích | Colab chạy được, không dùng eval để train, có metrics/ảnh eval và nhận xét lỗi | 10 |

## Điều kiện bắt buộc

- Thiếu quá 5 file nhãn hoặc không chạy qua `check_yolo_labels.py`: tối đa 49 điểm.
- Không có gold-set evaluation: tối đa 69 điểm.
- Dùng `eval` để train, thay đổi gold labels, hoặc cố truy vết/tìm nhãn ngoài repository: bài không được chấm phần pipeline; giảng viên xem xét theo quy định học phần.
- Model có mAP thấp không tự động bị trừ điểm nếu sinh viên giữ đúng split và phân tích được nguyên nhân. Mục tiêu là hiểu tác động của annotation, không phải benchmark mô hình trên 50 ảnh.

## Mức chất lượng annotation

| Mức | F1 @ IoU 0.50 | Mean IoU của matches | Diễn giải |
| --- | ---: | ---: | --- |
| Xuất sắc | >= 0.90 | >= 0.80 | bao phủ tốt, box rất sát và class nhất quán |
| Đạt | >= 0.80 | >= 0.70 | đủ điều kiện train |
| Cần sửa nhãn | F1 < 0.80 | hoặc mean IoU < 0.70 | tìm FN/FP/box lỏng, sửa rồi chạy lại; chỉ cần một trong hai chỉ số chưa đạt là phải sửa |
