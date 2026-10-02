@echo off
setlocal
echo Installing Python packages...
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
echo Building VideoToPPT.exe...
pyinstaller --noconfirm --clean --onefile --windowed --name VideoToPPT --collect-all cv2 --collect-all PIL app.py
echo.
echo Output: dist\VideoToPPT.exe
pause
