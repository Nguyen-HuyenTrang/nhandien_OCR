#!/bin/bash
# Script khởi động ứng dụng OCR trên Linux/macOS

echo "========================================"
echo "  Ứng dụng OCR Nhận dạng Nhãn Bưu kiện"
echo "========================================"
echo ""

# Kiểm tra Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] Python3 chưa được cài đặt!"
    echo "Vui lòng cài đặt Python3"
    exit 1
fi

echo "[OK] Python3 đã được cài đặt"
echo ""

# Kiểm tra Tesseract
if ! command -v tesseract &> /dev/null; then
    echo "[WARNING] Tesseract OCR chưa được cài đặt"
    echo "Ubuntu/Debian: sudo apt-get install tesseract-ocr tesseract-ocr-vie"
    echo "macOS: brew install tesseract tesseract-lang"
    echo ""
    echo "Tiếp tục chạy ứng dụng... (có thể gặp lỗi OCR)"
    echo ""
else
    echo "[OK] Tesseract OCR đã được cài đặt"
    echo ""
fi

# Kiểm tra virtual environment
if [ ! -d "venv" ]; then
    echo "[INFO] Tạo virtual environment..."
    python3 -m venv venv
    echo "[OK] Đã tạo virtual environment"
    echo ""
fi

# Kích hoạt virtual environment
echo "[INFO] Kích hoạt virtual environment..."
source venv/bin/activate

# Kiểm tra và cài đặt dependencies
echo "[INFO] Kiểm tra và cài đặt các thư viện cần thiết..."
pip install --upgrade pip > /dev/null 2>&1
pip install -r requirements.txt

echo ""
echo "[INFO] Khởi động ứng dụng..."
echo ""
echo "========================================"
echo "  Ứng dụng sẽ mở tại: http://localhost:8501"
echo "  Nhấn Ctrl+C để dừng ứng dụng"
echo "========================================"
echo ""

# Chạy ứng dụng Streamlit
streamlit run app.py

# Nếu có lỗi
if [ $? -ne 0 ]; then
    echo ""
    echo "[ERROR] Có lỗi khi chạy ứng dụng!"
    echo "Vui lòng kiểm tra log bên trên."
    exit 1
fi
