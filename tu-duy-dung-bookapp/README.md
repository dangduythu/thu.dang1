# Tư Duy Đúng / Think Right – Book App V2.7.2

V2.7.2 giữ nguyên toàn bộ nội dung song ngữ của V2.7 và sửa triệt để vấn đề layout/test bị treo từ V2.7.1.

## Sửa V2.7.2
- Chế độ BI tiếp tục hiển thị VI ở trên, EN ở dưới trong từng card.
- Bỏ toàn bộ cơ chế bind <Configure> + after_idle dùng để thay wraplength động.
- Dùng wrap text ổn định theo kích thước card, tránh vòng lặp layout của Tkinter.
- Không còn nguy cơ GUI test quay vô hạn do event storm.
- English trong card bên phải có đủ chiều ngang và tự xuống dòng.
- Giữ nguyên 40 bài, 40 stories, Quiz, Case Study, Tools, Glossary, Progress, bookmark và dữ liệu cũ.
- Giữ fix cuộn chuột và chống treo Treeview.

## Kiểm thử trước build
1. Syntax check toàn bộ module.
2. Validate toàn bộ dữ liệu song ngữ.
3. GUI regression test có log từng bước để xác định chính xác lỗi nếu có.
4. Timeout GUI test 2 phút.
5. Build EXE và xác nhận artifact.

Tên EXE: **TuDuyDung_BookApp_V2.7.2.exe**
