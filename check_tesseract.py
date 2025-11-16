"""
Script kiểm tra và cài đặt Tesseract OCR
"""
import sys
import subprocess
import os
from pathlib import Path

def check_tesseract_installed():
    """Kiểm tra Tesseract đã được cài đặt chưa"""
    print("=" * 60)
    print("KIỂM TRA TESSERACT OCR")
    print("=" * 60)
    print()
    
    # Kiểm tra tesseract command
    try:
        result = subprocess.run(['tesseract', '--version'], 
                              capture_output=True, 
                              text=True)
        print("✅ Tesseract đã được cài đặt!")
        print(f"\nVersion: {result.stdout.split()[1] if result.stdout else 'Unknown'}")
        return True
    except FileNotFoundError:
        print("❌ Tesseract CHƯA được cài đặt hoặc chưa có trong PATH!")
        return False

def check_tesseract_languages():
    """Kiểm tra các ngôn ngữ có sẵn"""
    print("\n" + "=" * 60)
    print("KIỂM TRA NGÔN NGỮ")
    print("=" * 60)
    print()
    
    try:
        result = subprocess.run(['tesseract', '--list-langs'], 
                              capture_output=True, 
                              text=True)
        
        if result.returncode == 0:
            langs = result.stdout.strip().split('\n')[1:]  # Skip first line
            print(f"✅ Tìm thấy {len(langs)} ngôn ngữ:")
            for lang in langs:
                print(f"  • {lang}")
            
            # Kiểm tra tiếng Việt
            if 'vie' in langs:
                print("\n✅ Ngôn ngữ tiếng Việt (vie) đã được cài đặt!")
                return True
            else:
                print("\n❌ CHƯA có ngôn ngữ tiếng Việt (vie)!")
                return False
        else:
            print("❌ Không thể liệt kê ngôn ngữ!")
            return False
            
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return False

def test_ocr_simple():
    """Test OCR đơn giản"""
    print("\n" + "=" * 60)
    print("TEST OCR CƠ BẢN")
    print("=" * 60)
    print()
    
    try:
        import pytesseract
        from PIL import Image
        import numpy as np
        
        # Tạo ảnh test đơn giản
        img = Image.new('RGB', (200, 50), color='white')
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "Hello World", fill='black')
        
        # Test OCR
        text = pytesseract.image_to_string(img, lang='eng')
        
        if text.strip():
            print(f"✅ OCR hoạt động! Nhận dạng: '{text.strip()}'")
            return True
        else:
            print("⚠️ OCR không nhận dạng được text")
            return False
            
    except ImportError as e:
        print(f"❌ Thiếu thư viện: {e}")
        print("Chạy: pip install pytesseract Pillow")
        return False
    except Exception as e:
        print(f"❌ Lỗi khi test OCR: {e}")
        return False

def print_installation_guide():
    """In hướng dẫn cài đặt"""
    print("\n" + "=" * 60)
    print("HƯỚNG DẪN CÀI ĐẶT TESSERACT OCR")
    print("=" * 60)
    print()
    
    print("📦 WINDOWS:")
    print("-" * 60)
    print("1. Download Tesseract installer:")
    print("   https://github.com/UB-Mannheim/tesseract/wiki")
    print()
    print("2. Chọn phiên bản mới nhất (ví dụ: tesseract-ocr-w64-setup-5.3.3.exe)")
    print()
    print("3. Khi cài đặt:")
    print("   ✅ Chọn 'Additional language data'")
    print("   ✅ Tick chọn 'Vietnamese' trong danh sách ngôn ngữ")
    print("   ✅ Cài đặt vào: C:\\Program Files\\Tesseract-OCR\\")
    print()
    print("4. Thêm vào System PATH:")
    print("   - Mở System Properties > Environment Variables")
    print("   - Thêm: C:\\Program Files\\Tesseract-OCR\\ vào PATH")
    print()
    print("5. KHỞI ĐỘNG LẠI Terminal/PowerShell")
    print()
    
    print("📦 LINUX (Ubuntu/Debian):")
    print("-" * 60)
    print("sudo apt-get update")
    print("sudo apt-get install tesseract-ocr")
    print("sudo apt-get install tesseract-ocr-vie")
    print()
    
    print("📦 macOS:")
    print("-" * 60)
    print("brew install tesseract")
    print("brew install tesseract-lang")
    print()

def check_config_file():
    """Kiểm tra file config"""
    print("\n" + "=" * 60)
    print("KIỂM TRA FILE CẤU HÌNH")
    print("=" * 60)
    print()
    
    config_path = Path(__file__).parent / "config" / "config.py"
    
    if config_path.exists():
        print(f"✅ Tìm thấy file config: {config_path}")
        
        # Đọc và kiểm tra TESSERACT_CMD
        with open(config_path, 'r', encoding='utf-8') as f:
            content = f.read()
            
        if 'TESSERACT_CMD' in content:
            # Tìm dòng TESSERACT_CMD
            for line in content.split('\n'):
                if 'TESSERACT_CMD' in line and not line.strip().startswith('#'):
                    print(f"\n📍 Đường dẫn hiện tại:")
                    print(f"   {line.strip()}")
                    
                    # Kiểm tra file có tồn tại không
                    if 'Windows' in line or 'Program Files' in line:
                        tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
                        if os.path.exists(tesseract_path):
                            print(f"\n✅ File Tesseract tồn tại tại: {tesseract_path}")
                        else:
                            print(f"\n❌ KHÔNG tìm thấy file: {tesseract_path}")
                            print("   Vui lòng cài đặt Tesseract hoặc cập nhật đường dẫn!")
                    break
        print()
    else:
        print(f"❌ Không tìm thấy file config: {config_path}")

def main():
    """Chạy tất cả kiểm tra"""
    print("\n")
    print("╔" + "═" * 58 + "╗")
    print("║" + " " * 10 + "CÔNG CỤ KIỂM TRA TESSERACT OCR" + " " * 18 + "║")
    print("╚" + "═" * 58 + "╝")
    print("\n")
    
    results = {
        'tesseract_installed': False,
        'vietnamese_available': False,
        'ocr_working': False
    }
    
    # Kiểm tra Tesseract
    results['tesseract_installed'] = check_tesseract_installed()
    
    if results['tesseract_installed']:
        # Kiểm tra ngôn ngữ
        results['vietnamese_available'] = check_tesseract_languages()
        
        # Test OCR
        results['ocr_working'] = test_ocr_simple()
    
    # Kiểm tra config
    check_config_file()
    
    # Tổng kết
    print("\n" + "=" * 60)
    print("KẾT QUẢ KIỂM TRA")
    print("=" * 60)
    print()
    
    if all(results.values()):
        print("✅✅✅ TẤT CẢ ĐỀU OK! Hệ thống sẵn sàng sử dụng!")
        print()
        print("Bạn có thể chạy ứng dụng:")
        print("  streamlit run app.py")
    else:
        print("⚠️ CÒN VẤN ĐỀ CẦN KHẮC PHỤC:")
        print()
        if not results['tesseract_installed']:
            print("❌ Tesseract chưa được cài đặt")
        if not results['vietnamese_available']:
            print("❌ Ngôn ngữ tiếng Việt chưa được cài đặt")
        if not results['ocr_working']:
            print("❌ OCR không hoạt động")
        
        print()
        print("👉 Xem hướng dẫn cài đặt bên dưới:")
        print_installation_guide()
    
    print("\n" + "=" * 60)
    print()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Đã dừng!")
    except Exception as e:
        print(f"\n❌ Lỗi: {e}")
        import traceback
        traceback.print_exc()
