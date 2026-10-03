# Tư Duy Đúng / Think Right – Book App V4.2

V4.2 tích hợp toàn bộ nền tảng V1.x–V2.7.x và các bước phát triển V2.8 → V4.2 thành một bản Windows duy nhất.

## Nền tảng được giữ nguyên
- 10 chương / 40 bài học Việt – Anh.
- 40 câu chuyện ghi nhớ.
- Sơ đồ ghi nhớ, khái niệm, cách áp dụng, ví dụ, checklist, bài tập, reflection.
- BI / VI / EN.
- Search, bookmark, đánh dấu đã đọc, lưu tiến độ.
- Quiz, Case Study cổ điển, Tools, Glossary.
- Layout song ngữ ổn định VI trên – EN dưới.
- Fix cuộn chuột và chống vòng lặp Treeview.

## Nâng cấp V2.8–V4.2
### Stable & Reading Experience
- Resume vị trí đọc theo từng bài.
- Focus Reading Mode ẩn menu/sidebar.
- Ghi chú cá nhân theo từng bài và xuất TXT.

### Learning Mode
- Quiz nâng từ 2 lên **4 câu/bài** cho đủ 40 bài.
- Smart Review bằng Flashcard + spaced repetition.
- Mỗi flashcard có mức Level, số lần ôn và ngày Due.

### Case Study V4.0
- Case Lab nhiều bước.
- Mỗi bước có quyết định, feedback và điểm tổng cuối case.
- Giữ Case Study cổ điển để đối chiếu.

### Workbench V4.2
7 worksheet có thể nhập và lưu trực tiếp:
1. 5 Why
2. PDCA
3. A3 Thinking
4. RACI
5. Risk Matrix
6. Decision Matrix
7. Skill Matrix

- Risk Matrix tự tính Initial Risk và Residual Risk.
- Decision Matrix tự tính weighted total từ Options / Criteria / Weights / Scores.
- Worksheet lưu trong dữ liệu app và có thể export TXT.

### Analytics
Dashboard bổ sung:
- Reading progress.
- Quiz completion / average.
- Case results.
- Flashcards due today.
- Notes count.
- Saved worksheets.

## Dữ liệu
Tiếp tục dùng:
%APPDATA%\TuDuyDungBookApp\state.json

Dữ liệu cũ từ V2.x vẫn được đọc; các trường V4.2 mới được bổ sung tự động.

## Build protection
GitHub Actions kiểm tra:
1. Syntax toàn bộ module.
2. 10 chương / 40 bài / song ngữ.
3. 4 quiz questions cho mỗi bài.
4. Flashcard/review schema.
5. Multi-step Case Lab.
6. 7 Workbench templates.
7. GUI smoke test cho lesson, quiz, review, case lab, workbench, notes và các tính năng cũ.
8. Build EXE + verify artifact.

Tên EXE: **TuDuyDung_BookApp_V4.2.exe**
