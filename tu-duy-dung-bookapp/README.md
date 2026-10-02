# Tư Duy Đúng / Think Right – Book App V2.7.1

V2.7.1 giữ nguyên toàn bộ nội dung và chức năng song ngữ của V2.7, đồng thời sửa lỗi chữ tiếng Anh bị tràn/cắt ở các card bên phải.

## Sửa giao diện V2.7.1
- Bỏ layout ép VI/EN thành hai cột hẹp bên trong các card nửa màn hình.
- Ở chế độ BI, mỗi card hiển thị **VI ở trên – EN ở dưới** với đường phân cách rõ ràng.
- Wrap text được tính theo **bề rộng thực tế của widget**, không còn dùng wraplength cố định.
- Resize cửa sổ vẫn tự điều chỉnh dòng chữ.
- Tiêu đề card cũng tự wrap theo độ rộng.
- Checklist và Common mistakes được render dạng responsive, không bị cắt phần English.
- Giữ nguyên BI / VI / EN, 40 bài, 40 stories, Quiz, Case Study, Tools, Glossary và Progress.
- Giữ toàn bộ fix cuộn chuột và chống treo Treeview từ các bản trước.

## Kiểm thử trước build
1. Syntax check toàn bộ module.
2. Validate đủ 40 bài và toàn bộ dữ liệu song ngữ.
3. GUI regression test ở chế độ BI/VI/EN.
4. Responsive test ở cửa sổ 1280×760 và 1500×940.
5. Build EXE và kiểm tra file đầu ra.

Tên EXE: **TuDuyDung_BookApp_V2.7.1.exe**
