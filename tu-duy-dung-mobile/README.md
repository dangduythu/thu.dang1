# Tư Duy Đúng Mobile V1.0

Bản điện thoại của **Tư Duy Đúng / Think Right – Book App V4.2**.

## Nguyên tắc mobile-first
- Một cột duy nhất; không ép hai cột Việt/Anh trên màn hình hẹp.
- Safe Area ở cả phía trên và dưới, không dính status bar/navigation bar.
- Nút bấm có vùng chạm tối thiểu 48px.
- Android Back và vuốt từ mép trái để quay lại.
- Ở Trang chủ, nút Back hỏi xác nhận thoát.
- Nội dung dài cuộn bằng một ScrollView chính, tránh nested-scroll lỗi.
- Bàn phím không che ô nhập ở Notes/Workbench.
- Tất cả dữ liệu học lưu offline bằng AsyncStorage.
- BI / VI / EN, Dark Mode, cỡ chữ, Focus Reading.
- Nhớ vị trí đọc theo từng bài.

## Tính năng giữ từ V4.2
- 10 chương / 40 bài song ngữ + 40 câu chuyện.
- Sơ đồ ghi nhớ theo dạng vertical cards phù hợp điện thoại.
- Quiz 4 câu/bài.
- Smart Review flashcard + spaced repetition.
- Case Lab nhiều bước.
- 7 Workbench: 5 Why, PDCA, A3, RACI, Risk, Decision, Skill Matrix.
- Notes, Tools, Glossary, Progress.
- Risk Matrix tính Initial/Residual Risk.
- Decision Matrix tính weighted total.
- Share worksheet/notes qua Share Sheet của điện thoại.

## Tạo dữ liệu
```
python scripts/export_content.py
```

## Chạy local
```
npm install
npx expo install react-native-safe-area-context @react-native-async-storage/async-storage
npx expo start
```

## APK
GitHub Actions workflow: **Build Tu Duy Dung Mobile Android**
Artifact: **TuDuyDung_Mobile_V1.0_APK**
