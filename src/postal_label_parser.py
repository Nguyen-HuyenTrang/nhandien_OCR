"""
Module phân tích và trích xuất thông tin từ nhãn bưu kiện
"""
import re
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PostalLabelParser:
    """Parser chuyên biệt cho nhãn bưu kiện"""

    def __init__(self):
        self.logger = logger

    def parse(self, text: str) -> dict:
        """
        Phân tích text OCR và trích xuất thông tin có cấu trúc

        Args:
            text: Text đã được OCR từ nhãn bưu kiện

        Returns:
            dict: Thông tin đã trích xuất
        """
        result = {
            'sender_name': '',
            'sender_address': '',
            'sender_phone': '',
            'recipient_name': '',
            'recipient_address': '',  # QUAN TRỌNG NHẤT - dùng để phân loại nội ô/ngoại ô
            'recipient_phone': '',
            'postal_code': '',
            'weight': '',
            'order_id': '',
        }

        try:
            # 1. Trích xuất thông tin chung trước
            result['order_id'] = self._extract_order_id(text)
            result['weight'] = self._extract_weight(text)

            # 2. Trích xuất tất cả số điện thoại
            all_phones = re.findall(r'0\d{9,10}', text)

            # 3. Tách thành 2 phần: Người gửi và Người nhận
            sender_section, recipient_section = self._split_sections(text)

            # 4. Trích xuất thông tin người gửi
            if sender_section:
                result['sender_name'] = self._extract_name_simple(sender_section, after='gửi')
                result['sender_address'] = self._extract_address_after_name(sender_section, result['sender_name'])
                # Lấy số điện thoại đầu tiên trong text (thường là người gửi)
                if len(all_phones) > 0:
                    result['sender_phone'] = all_phones[0]

            # 5. Trích xuất thông tin người nhận (QUAN TRỌNG NHẤT)
            if recipient_section:
                # Tập trung vào địa chỉ người nhận - dùng để phân loại nội ô/ngoại ô
                result['recipient_address'] = self._extract_address_after_name(recipient_section, '')
                # Các field khác ít quan trọng hơn
                result['recipient_name'] = self._extract_name_simple(recipient_section, after='nhận')
                if len(all_phones) > 1:
                    result['recipient_phone'] = all_phones[1]

            self.logger.info("Phân tích nhãn bưu kiện thành công")
            return result

        except Exception as e:
            self.logger.error(f"Lỗi khi phân tích: {e}")
            import traceback
            self.logger.error(traceback.format_exc())
            return result

    def _split_sections(self, text: str) -> tuple:
        """Tách text thành phần người gửi và người nhận"""
        # Tìm vị trí "Người gửi" và "Người nhận"
        sender_pos = -1
        recipient_pos = -1

        # Tìm "Người gửi"
        sender_match = re.search(r'Ng[ưu]+[oơ]+i\s+g[ửữ]+i', text, re.IGNORECASE)
        if sender_match:
            sender_pos = sender_match.start()

        # Tìm "Người nhận"
        recipient_match = re.search(r'Ng[ưu]+[oơ]+i\s+nh[ậa]+n', text, re.IGNORECASE)
        if recipient_match:
            recipient_pos = recipient_match.start()

        # Tách text
        if sender_pos >= 0 and recipient_pos >= 0:
            if sender_pos < recipient_pos:
                return text[sender_pos:recipient_pos], text[recipient_pos:]
            else:
                return text[sender_pos:], text[recipient_pos:sender_pos]
        elif sender_pos >= 0:
            return text[sender_pos:], ''
        elif recipient_pos >= 0:
            return '', text[recipient_pos:]
        else:
            # Không tìm thấy, tách đôi
            mid = len(text) // 2
            return text[:mid], text[mid:]

    def _extract_name_simple(self, text: str, after: str) -> str:
        """Trích xuất tên đơn giản - lấy từ sau keyword đến trước số hoặc keyword khác"""
        # VD: "Người gửi LUX PERFUMEE 92 trần..." → "LUX PERFUMEE"
        # VD: "Người nhận Bùi Tuấn Vũ D274A52..." → "Bùi Tuấn Vũ"

        # Tìm text sau keyword
        pattern = rf'{after}\s+([A-ZÀ-Ỹ][A-Za-zÀ-ỹ\s]+?)(?=\s*[A-Z]?\d|\s+Số|$)'
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            name = match.group(1).strip()
            # Loại bỏ số và ký tự lạ
            name = re.sub(r'\s*\d.*$', '', name)
            name = re.sub(r'\s+', ' ', name)
            # Lấy tối đa 5 từ
            words = [w for w in name.split()[:5] if not w.isdigit()]
            return ' '.join(words)

        return ''

    def _extract_address_after_name(self, text: str, name: str) -> str:
        """Trích xuất địa chỉ SAU tên - ƯU TIÊN địa chỉ người nhận"""
        # List tỉnh/thành phố mở rộng
        provinces = [
            'Hồ Chí Minh', 'Hà Nội', 'Đà Nẵng', 'Bình Dương', 'Đồng Nai',
            'Bà Rịa', 'Thủ Đầu Một', 'Cần Thơ', 'Hải Phòng', 'Long An'
        ]

        # Xác định vùng tìm kiếm
        search_text = text
        if name:
            name_pos = text.find(name)
            if name_pos >= 0:
                search_text = text[name_pos + len(name):]

        # Chiến lược 1: Tìm "Số" + số + ... + tỉnh (chuẩn địa chỉ VN)
        for province in provinces:
            if province in search_text:
                pattern = rf'(Số\s+\d+.{{10,}}?{province})'
                match = re.search(pattern, search_text, re.IGNORECASE)
                if match:
                    address = match.group(1)
                    # Làm sạch
                    address = re.sub(r'\s+', ' ', address)
                    # Cắt bỏ các keyword kết thúc
                    address = re.split(r'(?:Trọng lượng|Order|người nhận ký|Người nhận|\d{10,})', address, flags=re.IGNORECASE)[0]
                    address = address.strip(' ,.-')
                    if len(address) >= 20:
                        return address

        # Chiến lược 2: Tìm số 1-4 chữ số + text dài + tỉnh
        for province in provinces:
            if province in search_text:
                pattern = rf'(\d{{1,4}}\s+.{{15,}}?{province})'
                match = re.search(pattern, search_text, re.IGNORECASE)
                if match:
                    address = match.group(1)
                    address = re.sub(r'\s+', ' ', address)
                    address = re.split(r'(?:Trọng|Order|\d{{10,}})', address, flags=re.IGNORECASE)[0]
                    address = address.strip(' ,.-')
                    if len(address) >= 20:
                        return address

        return ''

    def _extract_name_from_section(self, section: str, person_type: str) -> str:
        """Trích xuất tên từ section"""
        # Tìm tên ngay sau "Người gửi" hoặc "Người nhận"
        # VD: "Người gửi LUX PERFUMEE 92 trần..." → "LUX PERFUMEE"
        # VD: "Người nhận Bùi Tuấn Vũ D274A52..." → "Bùi Tuấn Vũ"

        if person_type == 'gửi':
            pattern = r'g[ửữ]+i\s+([A-Z][A-Za-zÀ-ỹ\s]+?)(?=\s+\d+\s+[a-zà-ỹ]|\s*\d{2,}|$)'
        else:
            pattern = r'nh[ậa]+n\s+([A-Z][A-Za-zÀ-ỹ\s]+?)(?=\s+[A-Z]?\d|\s+[Ss]ố|$)'

        match = re.search(pattern, section, re.IGNORECASE)
        if match:
            name = match.group(1).strip()
            # Làm sạch
            name = re.sub(r'\s+', ' ', name)
            # Loại bỏ các từ chứa nhiều số
            words = []
            for word in name.split():
                # Chỉ lấy từ có ít hơn 30% ký tự là số
                digit_ratio = sum(c.isdigit() for c in word) / len(word) if word else 0
                if digit_ratio < 0.3:
                    words.append(word)

            # Lấy tối đa 5 từ
            name = ' '.join(words[:5])
            return name.strip()

        return ''

    def _extract_address_from_section(self, section: str) -> str:
        """Trích xuất địa chỉ từ section"""
        # Địa chỉ thường bắt đầu từ số nhà và có chứa: phường, quận, huyện, tỉnh, thành phố

        # Pattern: Số + tên đường/địa danh + phường/quận + tỉnh/TP
        patterns = [
            # Có số nhà và đầy đủ thông tin
            r'(\d+[A-Za-z,.\s]+(?:phường|quận|huyện)[^,\n]{5,}?(?:Hồ Chí Minh|Hà Nội|Đà Nẵng|Bình Dương|Thành Phố|Tỉnh)[^,\n]{0,30})',
            # Có "Số" và địa chỉ
            r'(Số\s+\d+[^,\n]{10,}?(?:Phường|Quận|Huyện)[^,\n]{5,})',
            # Từ số đến quận/huyện
            r'(\d+[^,\n]{10,}?(?:Quận|Huyện|Thành)[^,\n]{5,})',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, section, re.IGNORECASE)
            if matches:
                address = matches[0]
                # Làm sạch
                address = re.sub(r'\s+', ' ', address)
                # Cắt bỏ phần sau "Trọng lượng" hoặc "Order" nếu có
                address = re.split(r'(?:Trọng|Order|người nhận ký)', address, flags=re.IGNORECASE)[0]
                address = address.strip(' ,.')

                # Kiểm tra độ dài hợp lý
                if 15 < len(address) < 150:
                    return address

        return ''

    def _extract_phone_from_section(self, section: str, index: int = 0) -> str:
        """Trích xuất số điện thoại từ section"""
        phones = re.findall(r'0\d{9,10}', section)
        if phones and index < len(phones):
            return phones[index]
        return ''

    def _extract_order_id(self, text: str) -> str:
        """Trích xuất mã đơn hàng"""
        match = re.search(r'Order\s*[:\s]*(\d+)', text, re.IGNORECASE)
        if match:
            return match.group(1)
        return ''

    def _extract_weight(self, text: str) -> str:
        """Trích xuất trọng lượng"""
        match = re.search(r'[Tt]r[oọ]ng\s+l[uươ]+ng.*?(\d+[.,]\d+)\s*KG', text, re.IGNORECASE)
        if match:
            return match.group(1) + ' KG'
        return ''

    def _extract_postal_code(self, text: str) -> str:
        """Trích xuất mã bưu chính (5-6 số)"""
        # Tìm các chuỗi 5-6 số
        codes = re.findall(r'\b\d{5,6}\b', text)
        for code in codes:
            # Loại trừ số điện thoại (10-11 số)
            if len(code) <= 6:
                return code
        return ''


if __name__ == "__main__":
    # Test
    parser = PostalLabelParser()
    sample = """859347254543 859347254543 859347254543 đTikTokShop ET 859347254543 Người gửi LUX PERFUMEE 92 trần bá giao phường 5 gò vấp, Phường 05-028QGV05, Quận Gò Vấp, Hồ Chí Minh 800 Người nhận Bùi Tuấn Vũ D274A52 011 Số 96,D26, khu phố 1, Phường Hòa Phú-274TPT06,Thành Phố Thủ Dầu Một Bình Dương Trọng lượng tinh phi 0.059 KG người nhận ký: Order 579759172427744661 2025-07-26 13:44 kiên: 620"""

    result = parser.parse(sample)

    print("\n📤 NGƯỜI GỬI:")
    print(f"  Tên: {result['sender_name']}")
    print(f"  SĐT: {result['sender_phone']}")
    print(f"  Địa chỉ: {result['sender_address']}")

    print("\n📥 NGƯỜI NHẬN:")
    print(f"  Tên: {result['recipient_name']}")
    print(f"  SĐT: {result['recipient_phone']}")
    print(f"  Địa chỉ: {result['recipient_address']}")

    print("\n📦 THÔNG TIN:")
    print(f"  Order ID: {result['order_id']}")
    print(f"  Trọng lượng: {result['weight']}")
    print(f"  Mã bưu chính: {result['postal_code']}")
