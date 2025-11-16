@echo off
REM Script khởi động ứng dụng OCR trên Windows

echo ========================================
echo   Ung dung OCR Nhan dang Nhan Buu kien
echo ========================================
echo.

REM Kiểm tra Python
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python chua duoc cai dat!
    echo Vui long cai dat Python tu: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo [OK] Python da duoc cai dat
echo.

REM Kiểm tra Tesseract
tesseract --version >nul 2>&1
if errorlevel 1 (
    echo [WARNING] Tesseract OCR chua duoc cai dat hoac chua them vao PATH
    echo Vui long cai dat Tesseract tu: https://github.com/UB-Mannheim/tesseract/wiki
    echo.
    echo Tiep tuc chay ung dung... (co the gap loi OCR)
    echo.
) else (
    echo [OK] Tesseract OCR da duoc cai dat
    echo.
)

REM Kiểm tra virtual environment
if not exist "venv\" (
    echo [INFO] Tao virtual environment...
    python -m venv venv
    echo [OK] Da tao virtual environment
    echo.
)

REM Kích hoạt virtual environment
echo [INFO] Kich hoat virtual environment...
call venv\Scripts\activate.bat

REM Kiểm tra và cài đặt dependencies
echo [INFO] Kiem tra va cai dat cac thu vien can thiet...
pip install --upgrade pip >nul 2>&1
pip install -r requirements.txt

echo.
echo [INFO] Khoi dong ung dung...
echo.
echo ========================================
echo   Ung dung se mo tai: http://localhost:8501
echo   Nhan Ctrl+C de dung ung dung
echo ========================================
echo.

REM Chạy ứng dụng Streamlit
streamlit run app.py

REM Nếu có lỗi
if errorlevel 1 (
    echo.
    echo [ERROR] Co loi khi chay ung dung!
    echo Vui long kiem tra log ben tren.
    pause
)
