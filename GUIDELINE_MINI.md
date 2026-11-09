# Mini guideline — bài làm cá nhân

> Điền nội dung này trước khi bắt đầu gán nhãn. Giữ lại các quyết định sau khi self-QC.

## Định nghĩa lớp

| Lớp | Định nghĩa của bạn | Ví dụ/điểm phân biệt |
| --- | --- | --- |
| `car` (ID 0) | Xe con, sedan, SUV, taxi và xe bán tải. | Xe bán tải thuộc `car` theo schema của bài; không gán xe buýt, xe tải hoặc xe máy vào lớp này. |
| `truck` (ID 1) | Xe tải chở hàng và xe đầu kéo. | Phân biệt với xe bán tải thuộc `car` và xe van thuộc `van`; nếu hình ảnh không đủ rõ để phân lớp thì ghi lại để hỏi giảng viên. |
| `bus` (ID 2) | Xe buýt và minibus chở khách. | Phân biệt với van/minivan thuộc `van`; trường hợp khó phân biệt cần ghi tên ảnh và hỏi giảng viên, không tự đổi schema. |
| `van` (ID 3) | Xe van và minivan dùng chở hàng hoặc chở người. | Không phân lớp chỉ dựa vào việc chở hàng hay chở người; khi không chắc giữa `van`, `bus` và `car`, ghi lại trường hợp để hỏi giảng viên. |

## Quy tắc chung

- Box bám sát vật thể nghĩa là: mỗi xe hợp lệ có một khung chữ nhật riêng, ôm sát phần thân xe nhìn thấy được; hạn chế lấy thêm nền, mặt đường hoặc xe bên cạnh. Không gộp nhiều xe vào một box.
- Vật thể bị che khuất: vẫn gán nhãn nếu phần nhìn thấy đủ để nhận diện lớp. Vẽ box theo phần nhìn thấy, không suy đoán toàn bộ phần bị che. Hai xe chồng lên nhau phải có hai box riêng.
- Vật thể bị cắt bởi rìa ảnh: nếu nhận diện được lớp thì vẽ box quanh phần còn trong ảnh, chạm đúng mép ảnh; không kéo box vượt biên hoặc đoán phần nằm ngoài khung hình.
- Vật thể rất nhỏ/mơ hồ: không tự đoán khi không xác định chắc được lớp. Ghi tên ảnh, tình huống và câu hỏi để hỏi giảng viên; cập nhật quyết định sau khi được làm rõ.
- Xe đang đỗ: vẫn gán nhãn theo loại xe.
- Ngoài phạm vi: không gán người đi bộ, xe đạp, xe máy/mô tô, biển báo, đèn giao thông, ảnh xe trên quảng cáo hoặc xe phản chiếu trong kính/gương.
- Định dạng xuất: YOLO detection, thứ tự lớp cố định `car=0`, `truck=1`, `bus=2`, `van=3`. Mỗi ảnh có một file `.txt` cùng basename; ảnh không có xe hợp lệ vẫn có file rỗng.

## Ghi lại quyết định cho ít nhất ba ca mơ hồ

> Ghi các ca thực tế đã quan sát. Ca chưa chắc phải ghi rõ cần xác nhận; cập nhật quyết định sau khi tự kiểm tra hoặc hỏi giảng viên.

| Ảnh | Tình huống | Quyết định cuối | Lý do theo schema |
| --- | --- | --- | --- |
| `drive_007` | Xe limousine kiểu Việt Nam (thân cao, dạng van/minivan chở khách), dễ nhầm với `car` hoặc `bus`. | Gán `van` (ID 3); không gán `car`. | Schema: `van` gồm van/minivan chở hàng hoặc chở người; `car` chỉ sedan/SUV/taxi/bán tải. “Limousine” ở VN thường là van cao chở khách → thuộc `van`, không thuộc `car`. Chỉ chuyển sang `bus` nếu rõ là xe buýt/minibus lớn hơn. |
| `drive_016.jpg` | Xe nhỏ ở xa, sát mép trên ảnh (box 309 trong ảnh chụp CVAT), bị mờ nên khó phân biệt `truck`, `van` và `car`. Không thấy rõ cấu tạo khoang chở hàng. | Chưa chốt: nhãn hiện tại là `truck` (ID 1). Phóng to ảnh gốc và hỏi giảng viên trước khi xác nhận hoặc đổi lớp; không coi nhãn đang có là bằng chứng phân lớp đúng. | `truck` dành cho xe tải chở hàng/đầu kéo; `van` dành cho van/minivan; xe bán tải thuộc `car`. Cần dựa vào đặc điểm thân xe và khoang hàng nhìn thấy, không suy lớp từ kích thước box hoặc nhãn cũ. Box chỉ bao phần xe quan sát được và nằm trong biên ảnh. |
| `drive_046.jpg` | Xe ở xa phía trên bên trái ảnh (box 1004 trong ảnh chụp CVAT), kích thước nhỏ và mờ, nằm sát các xe khác nên khó phân biệt `car` với `van`. | Chưa chốt: nhãn hiện tại là `car` (ID 0). Phóng to ảnh gốc để kiểm tra đặc điểm thân xe; nếu vẫn không rõ thì hỏi giảng viên trước khi giữ hoặc đổi lớp. Vẽ box riêng cho từng xe, không gộp các xe liền nhau. | `car` gồm xe con/SUV/taxi/bán tải; `van` gồm van/minivan. Không suy lớp chỉ từ kích thước xe trong ảnh, vì xe ở xa có box rất nhỏ. Chỉ dùng phần nhìn thấy để phân lớp và vẽ khung; không đoán phần bị che. |
