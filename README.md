# Ứng dụng OCR Nhận dạng và Phân loại Nhãn Bưu kiện

## Mô tả

Ứng dụng sử dụng công nghệ OCR (Optical Character Recognition) để nhận dạng văn bản từ hình ảnh nhãn bưu kiện và tự động phân loại theo khu vực giao hàng.

## Tính năng

- ✅ Nhận dạng text từ hình ảnh nhãn bưu kiện
- ✅ Trích xuất thông tin địa chỉ, tên người nhận
- ✅ Phân loại theo khu vực giao hàng (Miền Bắc, Miền Trung, Miền Nam)
- ✅ Giao diện web thân thiện với người dùng
- ✅ Hỗ trợ nhiều định dạng ảnh (JPG, PNG, JPEG)

## Cấu trúc dự án

```
nhandien/
├── src/
│   ├── ocr_engine.py          # Module xử lý OCR
│   ├── region_classifier.py   # Module phân loại khu vực
│   └── image_processor.py     # Module xử lý ảnh
├── models/
│   └── region_mapping.json    # Dữ liệu ánh xạ khu vực
├── data/
│   ├── sample/                # Ảnh mẫu để test
│   └── output/                # Kết quả xử lý
├── config/
│   └── config.py              # Cấu hình ứng dụng
├── tests/
│   └── test_ocr.py           # Test cases
├── app.py                     # Ứng dụng Streamlit
├── requirements.txt           # Dependencies
└── README.md                  # Tài liệu hướng dẫn
```

## Cài đặt

### 1. Cài đặt Tesseract OCR

**Windows:**

- Download từ: https://github.com/UB-Mannheim/tesseract/wiki
- Cài đặt và thêm vào PATH

**Linux:**

```bash
sudo apt-get install tesseract-ocr tesseract-ocr-vie
```

### 2. Cài đặt Python packages

```bash
pip install -r requirements.txt
```

## Sử dụng

### Chạy ứng dụng web

```bash
streamlit run app.py
```

### Sử dụng trong code

```python
from src.ocr_engine import OCREngine
from src.region_classifier import RegionClassifier

# Khởi tạo
ocr = OCREngine()
classifier = RegionClassifier()

# Nhận dạng text
text = ocr.extract_text('path/to/image.jpg')

# Phân loại khu vực
region = classifier.classify(text)
print(f"Khu vực giao hàng: {region}")
```

## Công nghệ sử dụng

- **Python 3.12+**
- **Tesseract OCR**: Nhận dạng ký tự quang học
- **OpenCV**: Xử lý ảnh
- **Streamlit**: Giao diện web
- **Pandas**: Xử lý dữ liệu

## Tác giả

Phát triển theo kế hoạch chi tiết dự án OCR nhận dạng nhãn bưu kiện

## Giấy phép

MIT License
