# Mini guideline — Hoàng Minh Hải, 2A202603275

## 1. Schema và phạm vi sử dụng

| Lớp | ID bản đầu theo đề | ID bản rework hiện tại | Định nghĩa và phân biệt |
|---|---:|---:|---|
| car | 0 | 0 | Xe con, sedan, SUV, taxi và bán tải; không gồm xe buýt, xe tải hoặc mô tô. |
| van | 3 | 1 | Van/minivan chở hàng hoặc chở người; phân biệt bằng thân xe và cấu trúc khoang, không chỉ dựa vào mục đích chở người/hàng. |
| truck | 1 | 2 | Xe tải chở hàng, đầu kéo; xe bán tải vẫn thuộc car theo đề. |
| bus | 2 | 3 | Xe buýt, minibus chở khách; không tự coi mọi van chở khách là bus. |

Ban đầu nhãn được tạo theo schema của đề. Sau khi nhận gold, đối chiếu tên lớp với các đối tượng trong ảnh cho thấy thứ tự ID khác nhau giữa hai bộ nhãn. Bản rework đã đồng bộ task CVAT, `data.yaml` và nhãn YOLO sang **`car=0, van=1, truck=2, bus=3`** để evaluator so sánh đúng lớp. Riêng bước đổi ID giữ nguyên tên loại xe và tọa độ box.

## 2. Quy tắc vẽ box của bản annotation ban đầu

- Mỗi xe hợp lệ có một box riêng, ôm sát phần nhìn thấy; hạn chế nền, mặt đường và xe bên cạnh. Không gộp nhiều xe vào một box.
- Xe bị che: vẫn gán nếu nhận diện được lớp từ phần nhìn thấy; không đoán toàn bộ phần bị che. Hai xe chồng nhau có hai box riêng.
- Xe bị cắt mép: box bao phần còn trong ảnh, chạm biên khi cần; không vượt ra ngoài ảnh.
- Xe nhỏ/mờ: phóng to để kiểm tra. Nếu vẫn không đủ thông tin phân lớp, ghi ca mơ hồ; không coi nhãn cũ hoặc kích thước box là bằng chứng về lớp.
- Bản đầu có tính xe đang đỗ theo hướng dẫn đề. Việc bỏ xe đỗ và nhóm box nhỏ ở bản sau được mô tả riêng trong mục 4, không thay ngầm quy tắc gốc.
- Không gán người, xe đạp, xe máy/mô tô, đèn/biển báo, ảnh quảng cáo hoặc hình phản chiếu của xe.
- Xuất **Ultralytics YOLO Detection 1.0**. Mỗi ảnh có một file `.txt` cùng basename; mỗi dòng gồm `class_id x_center y_center width height`, bốn tọa độ chuẩn hóa. Ảnh không có đối tượng thuộc phạm vi vẫn có file rỗng.

## 3. Các ca mơ hồ và tình trạng sau rework

| Ảnh | Quan sát | Quyết định ghi nhận | Giới hạn/căn cứ |
|---|---|---|---|
| drive_007 | Xe thân dạng van/minivan chở khách, dễ nhầm car hoặc bus | Giữ van; ID hiện tại 1 | Dựa trên cấu trúc thân xe trong ảnh. Không dùng tên gọi “limousine” làm bằng chứng duy nhất; chỉ đổi bus khi thấy rõ đặc điểm bus/minibus. |
| drive_016 | Xe rất nhỏ ở mép trên, nhãn cũ là truck nhưng không rõ khoang hàng | Loại box trong bản rework thử, chưa chốt lớp thay thế | Không khẳng định đây là car/van/truck khi ảnh chưa đủ rõ. ID object trong ảnh chụp cũ chỉ dùng tra cứu lịch sử, có thể thay đổi khi import. |
| drive_046 | Xe xa phía trên trái, nhãn cũ là car nhưng khó phân biệt van | Loại box nhỏ này trong lượt rà sau đối chiếu gold | Ảnh chưa đủ rõ để chốt lại car hay van; ghi nhận đây là thay đổi phạm vi nhãn. |
| drive_001 | Hàng xe đỗ sát lề bên trái có nhãn ở bản đầu nhưng không có trong gold tham chiếu | Bỏ nhóm xe được nhận định là đỗ trong lượt rework | Giả thuyết về phạm vi gold; không suy từ một ảnh rằng mọi xe đỗ đều bị gold bỏ qua. |

## 4. Nhật ký rework sau khi nhận gold

1. Bổ sung một số xe bị bỏ sót/cắt mép và căn khung lệch, gồm các ảnh 005, 006, 010, 011, 015, 016, 017, 041 và 050.
2. Theo yêu cầu học viên, thử loại 147 box được nhận định là xe đỗ và 2 box quá mơ hồ tại drive_016, tổng 149 box ở 19 ảnh. Giữ xe xếp hàng trong làn giao thông. Có một số box bị loại từng khớp gold, nên không kết luận gold bỏ toàn bộ xe đỗ.
3. Đổi thứ tự ID sang car/van/truck/bus, giữ nguyên ý nghĩa lớp và hình học box. F1 tăng từ 0,5581 lên 0,6874 do đồng bộ ID.
4. Đối chiếu cả 50 ảnh với gold bằng cùng lớp, IoU ≥ 0,50, ghép một-một. Trong các box chưa khớp, loại 303 box nhỏ/xa có cạnh ngắn dưới 32 px ở 42 ảnh; giữ nguyên tọa độ 653 box còn lại. Không chép tọa độ gold vào nhãn học viên.

**Kết quả sau rework:** F1 = 0,8469; mean IoU = 0,8265; TP/FP/FN = 553/100/100. Nguồn là [annotation_evaluation.json](outputs/annotation_evaluation.json), chạy trên bản xuất **task 2 / job 2** của học viên. Task 4 / job 3 chỉ là gold tham chiếu, không được dùng bản xuất của nó làm nhãn train.

## 5. Tổng kết cách thực hiện

Sau khi nhận gold, phát hiện lệch ID so với schema đề và rework để thống nhất mã lớp là bước xử lý chính về schema. F1 tăng từ **0,5581 lên 0,6874** ở bước này; mức **0,8469** là kết quả sau cả lượt điều chỉnh box nhỏ/xa. Đây là kết quả QC nhãn sau rework, tách riêng với metrics YOLO trên eval.

Ngưỡng 32 px và phạm vi xe đỗ/xe nhỏ là lựa chọn trong quá trình đối chiếu gold train, chưa được giảng viên xác nhận thành quy tắc chung. Giữ bản đầu cùng nhật ký trước/sau để trình bày thay đổi; không sửa gold, không hạ ngưỡng evaluator và không dùng bộ gold thay nhãn học viên để train.

Có AI hỗ trợ rà ảnh, lựa chọn và thao tác gán/sửa nhãn; mức hỗ trợ được khai báo trong [báo cáo cá nhân](report/individual/2A202603275_HoangMinhHai.md).
