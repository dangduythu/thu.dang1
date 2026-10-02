# Tư Duy Đúng / Think Right – Book App V2.7

V2.7 là bản **song ngữ Việt – Anh toàn bộ chương trình**, phát triển từ V2.6 và giữ nguyên nội dung/tính năng cũ.

## Điểm mới V2.7
- Mặc định hiển thị **Song ngữ (BI)**.
- Có thể chuyển nhanh giữa **BI / VI / EN**.
- 10 chương và 40 bài học đều có bản tiếng Anh tương ứng.
- Toàn bộ 40 câu chuyện ghi nhớ được dịch sang tiếng Anh.
- Sơ đồ ghi nhớ hiển thị song ngữ.
- Các khối Khái niệm, Cách áp dụng, Tại sao quan trọng, Sai lầm, Ví dụ, Checklist, Bài tập và Reflection đều song ngữ.
- Quiz song ngữ cho toàn bộ 40 bài.
- 8 Case Study song ngữ.
- 15 Thinking & Management Tools song ngữ.
- Toàn bộ từ điển tích hợp có định nghĩa Việt – Anh.
- Trang chủ, mục lục, tiến độ, nút điều hướng và thông báo chính được thiết kế lại theo hướng song ngữ.
- Giữ cơ chế lưu progress/bookmark/quiz/case của các phiên bản trước.
- Giữ fix cuộn chuột và chống vòng lặp Treeview gây treo.

## Kiểm thử trước build
GitHub Actions bắt buộc chạy:
1. Syntax check toàn bộ module.
2. Validate đủ 10 chương / 40 bài.
3. Validate English translation coverage 1:1 cho 40 bài và 40 câu chuyện.
4. Validate toàn bộ glossary/tools/cases song ngữ.
5. GUI regression test ở BI, VI và EN.
6. Build EXE và xác nhận file đầu ra.

Tên EXE: **TuDuyDung_BookApp_V2.7.exe**
