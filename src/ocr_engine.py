"""
Module OCR Engine - Nhận dạng text từ hình ảnh
"""
import pytesseract
from PIL import Image
import cv2
import numpy as np
import logging
import os
import sys
from pathlib import Path

# Thêm thư mục config vào path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import TESSERACT_CMD, OCR_LANG, MIN_CONFIDENCE

# Cấu hình Tesseract
if os.path.exists(TESSERACT_CMD):
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OCREngine:
    """Engine xử lý OCR để nhận dạng text từ ảnh"""

    def __init__(self, lang: str = OCR_LANG):
        """
        Khởi tạo OCR Engine

        Args:
            lang: Ngôn ngữ nhận dạng (mặc định: vie+eng)
        """
        self.lang = lang
        self.logger = logger
        self.min_confidence = MIN_CONFIDENCE

        # Kiểm tra Tesseract
        self._check_tesseract()

    def _check_tesseract(self):
        """Kiểm tra Tesseract đã được cài đặt chưa"""
        try:
            version = pytesseract.get_tesseract_version()
            self.logger.info(f"✅ Tesseract version: {version}")

            # Kiểm tra ngôn ngữ có sẵn
            try:
                langs = pytesseract.get_languages()
                if 'vie' in langs:
                    self.logger.info("✅ Vietnamese language pack available")
                else:
                    self.logger.warning("⚠️ Vietnamese language pack not found. OCR accuracy may be reduced.")
            except:
                pass

        except Exception as e:
            self.logger.error(f"❌ Lỗi: Tesseract chưa được cài đặt hoặc cấu hình sai. {e}")
            self.logger.info("📋 Hướng dẫn cài đặt Tesseract:")
            self.logger.info("   Windows: https://github.com/UB-Mannheim/tesseract/wiki")
            self.logger.info("   Linux: sudo apt-get install tesseract-ocr tesseract-ocr-vie")
            raise RuntimeError("Tesseract OCR not properly configured")

    def extract_text(self, image_path, config: str = '--psm 6') -> str:
        """
        Trích xuất text từ ảnh

        Args:
            image_path: Đường dẫn đến ảnh hoặc numpy array
            config: Cấu hình Tesseract (PSM - Page Segmentation Mode)
                   --psm 3: Fully automatic (default)
                   --psm 6: Assume a single uniform block of text
                   --psm 11: Sparse text

        Returns:
            str: Text được nhận dạng
        """
        try:
            # Đọc ảnh nếu là đường dẫn, hoặc dùng trực tiếp nếu là numpy array
            if isinstance(image_path, str):
                image = Image.open(image_path)
            else:
                # Convert numpy array to PIL Image
                import cv2
                if len(image_path.shape) == 3:
                    image = Image.fromarray(cv2.cvtColor(image_path, cv2.COLOR_BGR2RGB))
                else:
                    image = Image.fromarray(image_path)

            # OCR với config
            text = pytesseract.image_to_string(
                image,
                lang=self.lang,
                config=config
            )

            self.logger.info(f"Trích xuất text thành công từ: {image_path}")
            return text.strip()

        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất text: {e}")
            return ""

    def extract_text_with_confidence(self, image_path) -> dict:
        """
        Trích xuất text kèm độ tin cậy

        Args:
            image_path: Đường dẫn đến ảnh hoặc numpy array

        Returns:
            dict: {
                'text': str,
                'confidence': float,
                'details': list of dict
            }
        """
        try:
            # Đọc ảnh nếu là đường dẫn, hoặc dùng trực tiếp nếu là numpy array
            if isinstance(image_path, str):
                image = Image.open(image_path)
            else:
                # Convert numpy array to PIL Image
                import cv2
                if len(image_path.shape) == 3:
                    image = Image.fromarray(cv2.cvtColor(image_path, cv2.COLOR_BGR2RGB))
                else:
                    image = Image.fromarray(image_path)

            # Lấy dữ liệu chi tiết
            data = pytesseract.image_to_data(
                image,
                lang=self.lang,
                output_type=pytesseract.Output.DICT
            )

            # Lọc các từ có độ tin cậy đủ
            filtered_text = []
            confidences = []
            details = []

            n_boxes = len(data['text'])
            for i in range(n_boxes):
                confidence = int(data['conf'][i])
                text = data['text'][i].strip()

                if confidence > 0 and text:
                    if confidence >= self.min_confidence:
                        filtered_text.append(text)
                        confidences.append(confidence)

                    details.append({
                        'text': text,
                        'confidence': confidence,
                        'left': data['left'][i],
                        'top': data['top'][i],
                        'width': data['width'][i],
                        'height': data['height'][i]
                    })

            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            result = {
                'text': ' '.join(filtered_text),
                'confidence': round(avg_confidence, 2),
                'details': details
            }

            self.logger.info(f"Độ tin cậy trung bình: {avg_confidence:.2f}%")
            return result

        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất text với confidence: {e}")
            return {'text': '', 'confidence': 0, 'details': []}

    def extract_structured_data(self, image_path: str) -> dict:
        """
        Trích xuất dữ liệu có cấu trúc từ nhãn bưu kiện

        Args:
            image_path: Đường dẫn đến ảnh hoặc text đã OCR

        Returns:
            dict: Thông tin được trích xuất
        """
        result = {
            'sender_name': '',
            'sender_address': '',
            'sender_phone': '',
            'recipient_name': '',
            'recipient_address': '',
            'recipient_phone': '',
            'postal_code': '',
            'weight': '',
            'order_id': '',
            'raw_text': '',
            'confidence': 0
        }

        try:
            # Lấy text với confidence (hoặc dùng text đã có)
            import os
            if isinstance(image_path, str) and os.path.isfile(image_path):
                # Là đường dẫn file ảnh
                ocr_result = self.extract_text_with_confidence(image_path)
                text = ocr_result['text']
                result['confidence'] = ocr_result['confidence']
            else:
                # Đã là text hoặc không phải file
                text = str(image_path)
                result['confidence'] = 0

            result['raw_text'] = text

            # Sử dụng PostalLabelParser để trích xuất thông tin
            from src.postal_label_parser import PostalLabelParser
            parser = PostalLabelParser()
            parsed = parser.parse(text)

            # Cập nhật result với dữ liệu đã parse
            result.update(parsed)

            self.logger.info("Trích xuất dữ liệu có cấu trúc thành công")
            return result

        except Exception as e:
            self.logger.error(f"Lỗi khi trích xuất dữ liệu có cấu trúc: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return result

    def _split_sender_recipient(self, text: str) -> tuple:
        """Tách text thành phần người gửi và người nhận"""
        import re

        # Tìm vị trí của "Người gửi" và "Người nhận"
        sender_match = re.search(r'Ng[ưu]+[oơ]+i\s+g[ửữ]+i', text, re.IGNORECASE)
        recipient_match = re.search(r'Ng[ưu]+[oơ]+i\s+nh[ậa]+n', text, re.IGNORECASE)

        if sender_match and recipient_match:
            sender_start = sender_match.start()
            recipient_start = recipient_match.start()

            if sender_start < recipient_start:
                sender_section = text[sender_start:recipient_start]
                recipient_section = text[recipient_start:]
            else:
                recipient_section = text[recipient_start:sender_start]
                sender_section = text[sender_start:]
        elif sender_match:
            sender_section = text[sender_match.start():]
            recipient_section = ''
        elif recipient_match:
            recipient_section = text[recipient_match.start():]
            sender_section = ''
        else:
            # Không tìm thấy, thử tách theo vị trí
            mid = len(text) // 2
            sender_section = text[:mid]
            recipient_section = text[mid:]

        return sender_section, recipient_section

    def _extract_name(self, text: str, person_type: str) -> str:
        """Trích xuất tên người từ text"""
        import re

        # Pattern: Người gửi/nhận + TÊN (viết hoa chữ cái đầu) + số/địa chỉ
        # VD: "Người gửi LUX PERFUMEE" hoặc "Người nhận Bùi Tuấn Vũ"
        if person_type == 'sender':
            # Tìm text sau "Người gửi" đến trước số hoặc địa chỉ
            pattern = r'Ng[ưu]+[oơ]+i\s+g[ửữ]+i\s+([A-Z][A-Za-zÀ-ỹ\s]+?)(?=\s*\d|\s+[pqthđ]|$)'
        else:
            # Tìm text sau "Người nhận" đến trước số hoặc địa chỉ
            pattern = r'Ng[ưu]+[oơ]+i\s+nh[ậa]+n\s+([A-Z][A-Za-zÀ-ỹ\s]+?)(?=\s*[A-Z]?\d|\s+[SsNn][ốoơ]|$)'

        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            # Loại bỏ số và ký tự lạ ở cuối
            name = re.sub(r'\s+\d.*$', '', name)
            name = re.sub(r'\s{2,}', ' ', name)
            # Chỉ lấy tối đa 5 từ (tên người thường không quá dài)
            words = name.split()
            if len(words) > 5:
                name = ' '.join(words[:5])
            return name.strip()

        return ''

    def _extract_address(self, text: str) -> str:
        """Trích xuất địa chỉ từ text"""
        import re

        # Tìm địa chỉ dựa trên keywords
        address_keywords = [
            r'(?:Số\s+)?(\d+[A-Z]?\d*[,\s]+[^,\n]+?(?:phường|phư[oơ]+ng|quận|qu[aậ]+n|huyện|huy[eệ]+n|thành phố|tỉnh|thị xã)[^,\n]*(?:,\s*[^,\n]+)*)',
            r'(\d+\s+[^,\n]+?(?:đường|[đd]u[oơ]+ng)[^,\n]*(?:,\s*[^,\n]+)*)',
            r'((?:phường|quận|huyện|thành phố|tỉnh)\s+[^,\n]+(?:,\s*[^,\n]+)*)'
        ]

        for pattern in address_keywords:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                # Lấy địa chỉ dài nhất (thường là đầy đủ nhất)
                address = max(matches, key=len)
                # Làm sạch địa chỉ
                address = re.sub(r'\s+', ' ', address)
                address = address.strip()
                return address

        # Fallback: tìm dòng có chứa địa chỉ
        lines = text.split('\n')
        for line in lines:
            line = line.strip()
            if any(kw in line.lower() for kw in ['phường', 'quận', 'huyện', 'tỉnh', 'thành phố']):
                # Loại bỏ số điện thoại và mã nếu có
                cleaned = re.sub(r'\b0\d{9,10}\b', '', line)
                cleaned = re.sub(r'\b\d{5,6}\b', '', cleaned)
                cleaned = re.sub(r'\s+', ' ', cleaned).strip()
                if len(cleaned) > 20:  # Địa chỉ phải có độ dài nhất định
                    return cleaned

        return ''

    def _is_phone_number(self, text: str) -> bool:
        """Kiểm tra xem text có chứa số điện thoại không"""
        import re
        # Tìm chuỗi số liên tiếp 10-11 chữ số bắt đầu bằng 0
        pattern = r'0\d{9,10}'
        return bool(re.search(pattern, text))

    def _extract_phone_number(self, text: str) -> str:
        """Trích xuất số điện thoại từ text"""
        import re

        # Pattern cho số điện thoại Việt Nam
        patterns = [
            r'0\d{9,10}',  # 10-11 số bắt đầu bằng 0
            r'\d{3}[-.\s]?\d{3}[-.\s]?\d{4}',  # Format có dấu phân cách
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                phone = match.group()
                # Loại bỏ ký tự đặc biệt
                return ''.join(c for c in phone if c.isdigit())

        return ''

    def _extract_postal_code(self, text: str) -> str:
        """Trích xuất mã bưu chính"""
        import re

        # Mã bưu chính Việt Nam: 5-6 số
        pattern = r'\b\d{5,6}\b'
        match = re.search(pattern, text)

        if match:
            return match.group()

        return ''

    def visualize_ocr_result(self, image_path: str, output_path: str) -> None:
        """
        Vẽ kết quả OCR lên ảnh

        Args:
            image_path: Đường dẫn ảnh gốc
            output_path: Đường dẫn lưu ảnh kết quả
        """
        try:
            # Đọc ảnh
            image = cv2.imread(image_path)

            # Lấy dữ liệu OCR
            pil_image = Image.open(image_path)
            data = pytesseract.image_to_data(
                pil_image,
                lang=self.lang,
                output_type=pytesseract.Output.DICT
            )

            # Vẽ bounding boxes
            n_boxes = len(data['text'])
            for i in range(n_boxes):
                confidence = int(data['conf'][i])
                text = data['text'][i].strip()

                if confidence > self.min_confidence and text:
                    x, y, w, h = (data['left'][i], data['top'][i],
                                 data['width'][i], data['height'][i])

                    # Vẽ rectangle
                    cv2.rectangle(image, (x, y), (x + w, y + h), (0, 255, 0), 2)

                    # Ghi text và confidence
                    label = f"{text} ({confidence}%)"
                    cv2.putText(image, label, (x, y - 10),
                              cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

            # Lưu ảnh
            cv2.imwrite(output_path, image)
            self.logger.info(f"Đã lưu ảnh visualization tại: {output_path}")

        except Exception as e:
            self.logger.error(f"Lỗi khi visualization: {e}")


if __name__ == "__main__":
    # Test
    ocr = OCREngine()
    print("OCREngine module loaded successfully!")
