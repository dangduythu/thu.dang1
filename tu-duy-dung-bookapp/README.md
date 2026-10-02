# Tư Duy Đúng – Book App V2.6

V2.6 phát triển từ V2.5.1 và tập trung làm mỗi bài học dễ nhớ hơn bằng **một câu chuyện ví dụ cụ thể**.

## Nội dung và tính năng
- 10 phần / 40 bài học.
- Mỗi bài có:
  - Sơ đồ ghi nhớ.
  - **Câu chuyện ghi nhớ riêng** với nhân vật/tình huống cụ thể.
  - Điểm cần nhớ rút ra từ câu chuyện.
  - Khái niệm.
  - Cách áp dụng.
  - Tại sao quan trọng.
  - Sai lầm thường gặp.
  - Ví dụ thực tế.
  - Checklist.
  - Bài tập áp dụng ngay.
  - Câu hỏi tự phản tư.
- Quiz cho đủ 40 bài.
- 8 Case Study.
- 15 Thinking & Management Tools.
- Từ điển 40 thuật ngữ.
- Dashboard tiến độ.
- Tìm kiếm, bookmark, đánh dấu đã đọc, chỉnh cỡ chữ.
- Giữ dữ liệu người dùng tại %APPDATA%\TuDuyDungBookApp\state.json.
- Giữ fix event-loop của V2.5.1 để tránh treo khi mở Học sách.
- Cuộn chuột/touchpad theo vùng con trỏ.

## Kiểm thử trước build
GitHub Actions bắt buộc:
1. Syntax check.
2. Validate đủ 10 chương / 40 bài.
3. Validate đủ **40 câu chuyện**, ID khớp chính xác với 40 bài.
4. Validate Quiz / Case / Tools / Glossary.
5. GUI smoke + event-loop regression test.
6. Build EXE và kiểm tra file đầu ra.

Tên EXE: TuDuyDung_BookApp_V2.6.exe
