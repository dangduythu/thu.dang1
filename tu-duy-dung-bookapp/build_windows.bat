@echo off
python -m pip install --upgrade pip
pip install -r requirements.txt
pyinstaller --noconfirm --clean --onefile --windowed --name "TuDuyDung_BookApp_V1.4.2" app.py
