# 🏗️ KIẾN TRÚC HỆ THỐNG - ỨNG DỤNG OCR NHẬN DẠNG NHÃN BƯU KIỆN

## 📐 TỔNG QUAN KIẾN TRÚC

```
┌─────────────────────────────────────────────────────────────────┐
│                     USER INTERFACE LAYER                        │
│                    (Streamlit Web App)                          │
│                         app.py                                  │
└────────────────┬────────────────────────────────────────────────┘
                 │
                 ↓
┌─────────────────────────────────────────────────────────────────┐
│                    APPLICATION LAYER                            │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ OCR Engine   │  │Image         │  │ Region       │        │
│  │              │  │Processor     │  │ Classifier   │        │
│  │ ocr_engine   │  │              │  │              │        │
│  │    .py       │  │image_        │  │region_       │        │
│  │              │  │processor.py  │  │classifier.py │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
│         │                  │                  │                 │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          ↓                  ↓                  ↓
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER                                 │
│                                                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐        │
│  │ Tesseract    │  │ OpenCV       │  │ JSON         │        │
│  │ OCR Engine   │  │ Library      │  │ Database     │        │
│  │              │  │              │  │              │        │
│  │ (External)   │  │ (cv2)        │  │region_       │        │
│  │              │  │              │  │mapping.json  │        │
│  └──────────────┘  └──────────────┘  └──────────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🔄 LUỒNG XỬ LÝ DỮ LIỆU

```
┌─────────────┐
│   User      │
│  Upload     │──┐
│   Image     │  │
└─────────────┘  │
                 ↓
         ┌──────────────┐
         │ Streamlit UI │
         │   (app.py)   │
         └──────┬───────┘
                │
                ↓
    ┌───────────────────────┐
    │  Image Preprocessing  │
    │  (image_processor.py) │
    │                       │
    │  • Grayscale         │
    │  • Denoise           │
    │  • Enhance Contrast  │
    │  • Threshold         │
    │  • Deskew            │
    └───────┬───────────────┘
            │
            ↓
    ┌───────────────────────┐
    │   OCR Processing      │
    │   (ocr_engine.py)     │
    │                       │
    │  • Tesseract OCR     │
    │  • Text Extraction   │
    │  • Confidence Calc   │
    │  • Data Structuring  │
    └───────┬───────────────┘
            │
            ↓
    ┌───────────────────────┐
    │ Region Classification │
    │(region_classifier.py) │
    │                       │
    │  • Province Match    │
    │  • Keyword Match     │
    │  • Postal Code Match │
    │  • Confidence Score  │
    └───────┬───────────────┘
            │
            ↓
    ┌───────────────────────┐
    │   Result Display      │
    │                       │
    │  • Region Info       │
    │  • OCR Text          │
    │  • Structured Data   │
    │  • Visualization     │
    └───────────────────────┘
```

---

## 📦 CHI TIẾT CÁC MODULE

### 1. OCREngine Module

```
┌──────────────────────────────────────┐
│         OCREngine Class              │
├──────────────────────────────────────┤
│ Attributes:                          │
│  • lang: str                         │
│  • min_confidence: int               │
│  • logger: Logger                    │
├──────────────────────────────────────┤
│ Methods:                             │
│  + extract_text()                    │
│  + extract_text_with_confidence()    │
│  + extract_structured_data()         │
│  + visualize_ocr_result()            │
│  - _is_phone_number()                │
│  - _extract_phone_number()           │
│  - _extract_postal_code()            │
└──────────────────────────────────────┘
         │
         ↓
    ┌────────────┐
    │ Tesseract  │
    │    OCR     │
    └────────────┘
```

**Luồng xử lý:**

1. Nhận ảnh đầu vào
2. Cấu hình Tesseract (PSM, language)
3. Chạy OCR
4. Parse kết quả
5. Tính confidence
6. Trích xuất thông tin có cấu trúc
7. Trả về kết quả

---

### 2. ImageProcessor Module

```
┌──────────────────────────────────────┐
│      ImageProcessor Class            │
├──────────────────────────────────────┤
│ Methods:                             │
│  + preprocess_image()                │
│  + resize_image()                    │
│  + rotate_image()                    │
│  + detect_and_correct_skew()         │
│  + crop_border()                     │
│  + save_processed_image()            │
│  - _auto_process()                   │
│  - _convert_to_grayscale()           │
│  - _apply_threshold()                │
│  - _denoise()                        │
└──────────────────────────────────────┘
         │
         ↓
    ┌────────────┐
    │  OpenCV    │
    │   (cv2)    │
    └────────────┘
```

**Pipeline xử lý:**

1. **Load Image** → Read image file
2. **Grayscale** → Convert to grayscale
3. **Denoise** → Remove noise (fastNlMeansDenoising)
4. **Enhance** → Increase contrast (CLAHE)
5. **Threshold** → Adaptive thresholding
6. **Morphology** → Clean up (morphologyEx)
7. **Deskew** → Correct rotation
8. **Save** → Output processed image

---

### 3. RegionClassifier Module

```
┌──────────────────────────────────────┐
│     RegionClassifier Class           │
├──────────────────────────────────────┤
│ Attributes:                          │
│  • region_data: dict                 │
│  • logger: Logger                    │
├──────────────────────────────────────┤
│ Methods:                             │
│  + classify()                        │
│  + get_all_regions()                 │
│  + get_region_info()                 │
│  + get_provinces_by_region()         │
│  - _normalize_text()                 │
│  - _classify_by_province()           │
│  - _classify_by_keywords()           │
│  - _classify_by_postal_code()        │
└──────────────────────────────────────┘
         │
         ↓
    ┌────────────────┐
    │ region_mapping │
    │     .json      │
    └────────────────┘
```

**Thuật toán phân loại:**

```
Input: OCR Text
  │
  ↓
┌────────────────────┐
│ Normalize Text     │ → lowercase, remove extra spaces
└──────┬─────────────┘
       │
       ├──→ Method 1: Province Matching
       │    • Exact match: confidence = 0.9
       │    • Partial match: confidence = 0.7
       │
       ├──→ Method 2: Keyword Matching
       │    • Count keyword matches
       │    • confidence = matches / total
       │
       └──→ Method 3: Postal Code
            • Extract 5-6 digit codes
            • Match prefix with region
            • confidence = 0.7
  │
  ↓
Select highest confidence
  │
  ↓
Return Classification Result
```

---

## 🎨 GIAO DIỆN NGƯỜI DÙNG (Streamlit)

```
┌─────────────────────────────────────────────────────┐
│              📦 HEADER SECTION                      │
│     Ứng dụng OCR Nhận dạng Nhãn Bưu kiện           │
└─────────────────────────────────────────────────────┘

┌──────────────┬──────────────────────────────────────┐
│   SIDEBAR    │          MAIN CONTENT                │
│              │                                      │
│ ⚙️ Cấu hình  │  ┌────────────────────────────────┐ │
│              │  │  📤 Upload Section            │ │
│ 📍 Khu vực   │  │  • File uploader              │ │
│   - Miền Bắc │  │  • Image preview              │ │
│   - M. Trung │  │  • Process button             │ │
│   - Miền Nam │  └────────────────────────────────┘ │
│              │                                      │
│ 📖 Hướng dẫn │  ┌────────────────────────────────┐ │
│              │  │  📊 Results Section           │ │
│ ℹ️ Thông tin  │  │  • Region info card           │ │
│              │  │  • OCR text expander          │ │
│              │  │  • Structured data            │ │
│              │  │  • Processed image            │ │
│              │  │  • Download buttons           │ │
│              │  └────────────────────────────────┘ │
└──────────────┴──────────────────────────────────────┘
```

**UI Components:**

- **Header**: Tiêu đề và icon
- **Sidebar**: Cấu hình, thông tin khu vực, hướng dẫn
- **Upload Section**: Upload file, preview, button
- **Results Section**: Hiển thị kết quả đa dạng
- **Download Section**: Nút download kết quả

---

## 💾 CẤU TRÚC DỮ LIỆU

### Input Data (Image)

```json
{
  "format": "JPG/PNG/BMP",
  "resolution": ">=300 DPI",
  "size": "<=5MB",
  "requirements": ["Clear text", "Good contrast", "Minimal skew"]
}
```

### OCR Result

```json
{
  "text": "Full extracted text",
  "confidence": 92.5,
  "details": [
    {
      "text": "word",
      "confidence": 95,
      "left": 100,
      "top": 200,
      "width": 50,
      "height": 20
    }
  ]
}
```

### Structured Data

```json
{
  "recipient_name": "Nguyễn Văn A",
  "phone": "0987654321",
  "address": "123 Đường XYZ, Quận 1",
  "postal_code": "70000",
  "raw_text": "...",
  "confidence": 88.5
}
```

### Classification Result

```json
{
  "region": "mien_nam",
  "region_name": "Miền Nam",
  "confidence": 0.95,
  "province": "TP. Hồ Chí Minh",
  "matched_keywords": ["Hồ Chí Minh", "Sài Gòn"]
}
```

---

## 🔧 CẤU HÌNH HỆ THỐNG

### config.py Structure

```python
# Đường dẫn
BASE_DIR: Path
DATA_DIR: Path
MODELS_DIR: Path

# Tesseract
TESSERACT_CMD: str
OCR_LANG: str

# Image Processing
IMAGE_EXTENSIONS: list
MAX_IMAGE_SIZE: tuple

# Classification
REGION_MAPPING_FILE: Path
MIN_CONFIDENCE: int

# Keywords
ADDRESS_KEYWORDS: list
RECIPIENT_KEYWORDS: list
PHONE_KEYWORDS: list
```

### region_mapping.json Structure

```json
{
  "provinces": {
    "mien_bac": {
      "name": "Miền Bắc",
      "code": "MB",
      "provinces": ["Hà Nội", "..."]
    },
    "..."
  },
  "districts": {
    "ha_noi": ["Ba Đình", "..."]
  },
  "postal_codes": {
    "mien_bac": ["10", "11", "..."]
  },
  "keywords": {
    "north": ["hà nội", "..."],
    "..."
  }
}
```

---

## 🔐 BẢO MẬT VÀ HIỆU NĂNG

### Bảo mật:

- ✅ Không lưu trữ ảnh người dùng lâu dài
- ✅ Xử lý local, không gửi dữ liệu ra ngoài
- ✅ Tự động xóa file tạm sau xử lý
- ✅ Không log thông tin nhạy cảm

### Tối ưu hiệu năng:

- ✅ Cache engines với @st.cache_resource
- ✅ Resize ảnh lớn trước khi xử lý
- ✅ Sử dụng adaptive thresholding
- ✅ Parallel processing khi có thể
- ✅ Lazy loading cho UI components

---

## 📊 GIÁM SÁT VÀ LOGGING

```
┌──────────────────────────────────────┐
│         Logging System               │
├──────────────────────────────────────┤
│ Level: INFO                          │
│                                      │
│ Logged Events:                       │
│  • Image upload                      │
│  • Processing start/end              │
│  • OCR confidence                    │
│  • Classification result             │
│  • Errors and warnings               │
│                                      │
│ Output: Console + File (optional)    │
└──────────────────────────────────────┘
```

---

## 🧪 TESTING ARCHITECTURE

```
┌──────────────────────────────────────┐
│         Test Suite                   │
├──────────────────────────────────────┤
│                                      │
│ • Unit Tests                         │
│   - test_region_classifier()         │
│   - test_image_processor()           │
│                                      │
│ • Integration Tests                  │
│   - test_full_pipeline()             │
│                                      │
│ • UI Tests (Manual)                  │
│   - test_streamlit_app()             │
│                                      │
└──────────────────────────────────────┘
```

---

## 🚀 DEPLOYMENT OPTIONS

### Option 1: Local Development

```bash
streamlit run app.py
```

### Option 2: Docker Container

```dockerfile
FROM python:3.12
RUN apt-get install tesseract-ocr
COPY . /app
WORKDIR /app
RUN pip install -r requirements.txt
CMD ["streamlit", "run", "app.py"]
```

### Option 3: Cloud Deployment

- **Streamlit Cloud**: Miễn phí, dễ deploy
- **Heroku**: Cần buildpack cho Tesseract
- **AWS/GCP**: Full control, tốn phí

---

## 📈 SCALABILITY CONSIDERATIONS

### Horizontal Scaling:

- ✅ API wrapper để xử lý batch
- ✅ Queue system (Celery/RabbitMQ)
- ✅ Load balancer cho multiple instances
- ✅ Database cho lưu trữ kết quả

### Vertical Scaling:

- ✅ GPU acceleration cho OpenCV
- ✅ Multi-threading cho OCR
- ✅ Caching strategies
- ✅ CDN cho static assets

---

**© 2024 Ứng dụng OCR Nhận dạng Nhãn Bưu kiện - System Architecture**
