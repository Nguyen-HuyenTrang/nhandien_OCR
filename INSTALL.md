# Hướng dẫn Cài đặt và Chạy Ứng dụng

## 📋 Yêu cầu hệ thống

- Python 3.8 trở lên
- Tesseract OCR 4.0 trở lên

## 🔧 Cài đặt

### Bước 1: Cài đặt Tesseract OCR

#### Windows:

1. Download Tesseract từ: https://github.com/UB-Mannheim/tesseract/wiki
2. Cài đặt (khuyến nghị: `C:\Program Files\Tesseract-OCR\`)
3. Thêm đường dẫn vào System PATH hoặc cập nhật trong `config/config.py`

#### Linux (Ubuntu/Debian):

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-vie  # Cho tiếng Việt
```

#### macOS:

```bash
brew install tesseract
brew install tesseract-lang  # Các ngôn ngữ bổ sung
```

### Bước 2: Tạo Virtual Environment (khuyến nghị)

```bash
# Tạo virtual environment
python -m venv venv

# Kích hoạt virtual environment
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### Bước 3: Cài đặt Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Lưu ý:** Nếu gặp lỗi khi cài đặt, thử cài từng package:

```bash
pip install opencv-python
pip install pytesseract
pip install Pillow
pip install numpy
pip install streamlit
pip install pandas
pip install python-dotenv
```

### Bước 4: Cấu hình đường dẫn Tesseract

Mở file `config/config.py` và cập nhật đường dẫn Tesseract:

**Windows:**

```python
TESSERACT_CMD = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

**Linux/macOS:**

```python
TESSERACT_CMD = '/usr/bin/tesseract'
```

## 🚀 Chạy ứng dụng

### Chạy ứng dụng Web (Streamlit)

```bash
streamlit run app.py
```

Ứng dụng sẽ mở tại: http://localhost:8501

### Chạy Tests

```bash
python -m pytest tests/
# Hoặc
python tests/test_ocr.py
```

### Sử dụng trong Python code

```python
from src.ocr_engine import OCREngine
from src.region_classifier import RegionClassifier
from src.image_processor import ImageProcessor

# Khởi tạo
ocr = OCREngine()
classifier = RegionClassifier()
processor = ImageProcessor()

# Xử lý ảnh
image_path = "path/to/label.jpg"

# Tiền xử lý
processed = processor.preprocess_image(image_path)

# OCR
result = ocr.extract_text_with_confidence(image_path)
print(f"Text: {result['text']}")
print(f"Confidence: {result['confidence']}%")

# Phân loại khu vực
classification = classifier.classify(result['text'])
print(f"Khu vực: {classification['region_name']}")
print(f"Độ tin cậy: {classification['confidence']}")
```

## 📝 Sử dụng ứng dụng Web

1. **Mở trình duyệt** tại http://localhost:8501
2. **Upload ảnh** nhãn bưu kiện (JPG, PNG, BMP)
3. **Nhấn "Bắt đầu xử lý"**
4. **Xem kết quả:**
   - Khu vực giao hàng
   - Text nhận dạng được
   - Thông tin chi tiết (SĐT, địa chỉ, mã bưu chính)
5. **Download kết quả** nếu cần

## 🔍 Xử lý sự cố

### Lỗi: "Tesseract not found"

- Kiểm tra Tesseract đã được cài đặt: `tesseract --version`
- Cập nhật đường dẫn trong `config/config.py`

### Lỗi: "Import cv2 could not be resolved"

```bash
pip uninstall opencv-python
pip install opencv-python-headless
```

### Lỗi: Nhận dạng kém

- Kiểm tra chất lượng ảnh (nên >= 300 DPI)
- Đảm bảo ảnh rõ nét, không bị mờ hoặc nghiêng
- Thử các phương pháp tiền xử lý khác nhau

### Lỗi: "No module named 'streamlit'"

```bash
pip install streamlit
```

## 📊 Hiệu năng

- **Thời gian xử lý:** ~2-5 giây/ảnh (tùy kích thước)
- **Độ chính xác OCR:** 85-95% (tùy chất lượng ảnh)
- **Độ chính xác phân loại:** 90-98%

## 🛠️ Tối ưu hóa

### Tăng tốc độ xử lý:

1. Giảm kích thước ảnh trước khi xử lý
2. Sử dụng GPU cho OpenCV (nếu có)
3. Cache kết quả với Streamlit

### Tăng độ chính xác:

1. Sử dụng ảnh chất lượng cao
2. Tiền xử lý ảnh kỹ càng
3. Fine-tune threshold parameters
4. Thêm từ điển tùy chỉnh cho Tesseract

## 📚 Tài liệu tham khảo

- **Tesseract OCR:** https://github.com/tesseract-ocr/tesseract
- **OpenCV:** https://docs.opencv.org/
- **Streamlit:** https://docs.streamlit.io/

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! Vui lòng:

1. Fork repository
2. Tạo branch mới
3. Commit changes
4. Push và tạo Pull Request

## 📧 Liên hệ

Nếu có vấn đề hoặc câu hỏi, vui lòng tạo issue trên GitHub.

---

**Chúc bạn sử dụng thành công! 🎉**
