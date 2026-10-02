@echo off
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m py_compile app.py content.py learning_data.py validate.py
python validate.py
pyinstaller --noconfirm --clean --onefile --windowed --name "TuDuyDung_BookApp_V2.5.1" app.py
