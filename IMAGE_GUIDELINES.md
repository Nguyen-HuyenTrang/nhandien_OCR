# 📸 HƯỚNG DẪN CHỤP ẢNH ĐỂ OCR CHÍNH XÁC

## ✅ Các yếu tố quan trọng cho kết quả OCR tốt:

### 1. **Ánh sáng**
- ✅ Chụp ở nơi có **ánh sáng đủ** (tự nhiên hoặc đèn trắng)
- ❌ Tránh chụp ngược sáng
- ❌ Tránh bóng đổ lên nhãn

### 2. **Góc chụp**
- ✅ Chụp **vuông góc** với nhãn (không chụp xiên)
- ✅ Nhãn nằm **phẳng**, không bị nhăn, gấp
- ❌ Tránh chụp góc nghiêng

### 3. **Độ phân giải**
- ✅ Dùng camera có **độ phân giải tốt** (>= 8MP)
- ✅ Chữ rõ nét, không bị mờ
- ❌ Tránh ảnh quá nhỏ hoặc quá mờ

### 4. **Khoảng cách**
- ✅ Chụp **đủ gần** để chữ rõ ràng
- ✅ Nhãn chiếm **60-80%** khung hình
- ❌ Không chụp quá xa (chữ nhỏ)

### 5. **Tiêu điểm**
- ✅ **Focus vào text** trên nhãn
- ❌ Tránh ảnh bị mất nét

## 🔧 Cài đặt tiền xử lý ảnh

Trong file `app.py`, có thể thay đổi method xử lý:

```python
# KHUYẾN NGHỊ: minimal - giữ nguyên ảnh gốc
processed = processor.preprocess_image(str(temp_path), method='minimal')

# Các option khác:
# method='auto' - tăng contrast (dùng khi ảnh mờ)
# method='grayscale' - chuyển xám (dùng khi ảnh đen trắng)
# method='threshold' - nhị phân hóa (CHỈ dùng khi ảnh RẤT rõ)
```

## 📝 Tips để cải thiện kết quả:

1. **Chụp nhiều ảnh** và chọn ảnh rõ nhất
2. **Làm phẳng nhãn** trước khi chụp
3. **Dùng giá đỡ** hoặc bề mặt cứng để tránh rung
4. **Test với method khác nhau** nếu kết quả không tốt
5. **Chụp ảnh màu** (không chuyển xám trước khi upload)

## 🎯 Ví dụ ảnh tốt vs xấu:

### ✅ Ảnh TỐT:
- Ánh sáng đều, không có bóng
- Chữ rõ ràng, màu sắc tươi sáng
- Nhãn phẳng, vuông góc
- Độ phân giải cao (>= 1920x1080)

### ❌ Ảnh XẤU:
- Tối, mờ, có bóng
- Chụp nghiêng, chữ bị méo
- Nhãn nhăn, gấp
- Ảnh quá nhỏ (<800x600)

## 🚀 Nếu kết quả vẫn không tốt:

1. **Thử lại với ảnh chất lượng cao hơn**
2. **Thay đổi method xử lý** trong code
3. **Kiểm tra Tesseract Vietnamese language** đã cài đúng chưa
4. **Thử với ảnh khác** để so sánh
