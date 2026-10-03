@echo off
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m py_compile app.py content.py stories.py learning_data.py i18n_en.py i18n_extra.py v42_data.py v42_ui.py validate.py
python validate.py
pyinstaller --noconfirm --clean --onefile --windowed --name "TuDuyDung_BookApp_V4.2" app.py
