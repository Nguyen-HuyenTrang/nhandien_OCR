"""
Cấu hình cho ứng dụng OCR nhận dạng nhãn bưu kiện
"""
import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).resolve().parent.parent

# Đường dẫn thư mục
DATA_DIR = BASE_DIR / "data"
SAMPLE_DIR = DATA_DIR / "sample"
OUTPUT_DIR = DATA_DIR / "output"
MODELS_DIR = BASE_DIR / "models"

# Tạo thư mục nếu chưa tồn tại
os.makedirs(SAMPLE_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Cấu hình Tesseract OCR
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'  # Windows
# TESSERACT_CMD = '/usr/bin/tesseract'  # Linux

# Ngôn ngữ OCR (vi = Tiếng Việt, eng = English)
OCR_LANG = 'vie+eng'

# Cấu hình xử lý ảnh
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']
MAX_IMAGE_SIZE = (1920, 1080)  # Max width, height

# Cấu hình phân loại khu vực
REGION_MAPPING_FILE = MODELS_DIR / "region_mapping.json"

# Cấu hình Streamlit
APP_TITLE = "Ứng dụng OCR Nhận dạng Nhãn Bưu kiện"
APP_ICON = "📦"

# Độ tin cậy tối thiểu để chấp nhận kết quả OCR (0-100)
MIN_CONFIDENCE = 60

# Keywords để phát hiện thông tin quan trọng
ADDRESS_KEYWORDS = ['địa chỉ', 'address', 'đường', 'phường', 'quận', 'huyện', 'tỉnh', 'thành phố']
RECIPIENT_KEYWORDS = ['người nhận', 'recipient', 'tên', 'name']
PHONE_KEYWORDS = ['điện thoại', 'phone', 'sdt', 'số điện thoại']
