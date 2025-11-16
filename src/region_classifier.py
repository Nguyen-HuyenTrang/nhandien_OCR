"""
Module phân loại khu vực giao hàng
"""
import json
import logging
import re
from pathlib import Path
import sys

# Thêm thư mục config vào path
sys.path.append(str(Path(__file__).parent.parent))
from config.config import REGION_MAPPING_FILE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RegionClassifier:
    """Phân loại nhãn bưu kiện theo khu vực giao hàng"""

    def __init__(self):
        """Khởi tạo Region Classifier"""
        self.logger = logger
        self.region_data = self._load_region_data()

    def _load_region_data(self) -> dict:
        """Load dữ liệu ánh xạ khu vực từ file JSON"""
        try:
            with open(REGION_MAPPING_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
            self.logger.info("Đã load dữ liệu khu vực thành công")
            return data
        except Exception as e:
            self.logger.error(f"Lỗi khi load dữ liệu khu vực: {e}")
            return {}

    def classify(self, text: str) -> dict:
        """
        Phân loại khu vực dựa trên text

        Args:
            text: Text được OCR từ nhãn bưu kiện

        Returns:
            dict: {
                'region': str (mien_bac/mien_trung/mien_nam),
                'region_name': str,
                'confidence': float,
                'province': str,
                'matched_keywords': list,
                'area_type': str (noi_o/ngoai_o),  # THÊM MỚI
                'area_name': str  # THÊM MỚI
            }
        """
        result = {
            'region': 'unknown',
            'region_name': 'Không xác định',
            'confidence': 0.0,
            'province': '',
            'matched_keywords': [],
            'area_type': 'unknown',
            'area_name': 'Không xác định'
        }

        if not text:
            return result

        # Chuẩn hóa text
        text_lower = self._normalize_text(text)

        # Phân loại theo tỉnh/thành phố
        province_result = self._classify_by_province(text_lower)
        if province_result['confidence'] > 0:
            result.update(province_result)
            # Phân loại NỘI Ô / NGOẠI Ô
            area_result = self._classify_urban_suburban(text_lower, result.get('province', ''))
            result.update(area_result)
            return result

        # Phân loại theo keywords
        keyword_result = self._classify_by_keywords(text_lower)
        if keyword_result['confidence'] > 0:
            result.update(keyword_result)
            # Phân loại NỘI Ô / NGOẠI Ô
            area_result = self._classify_urban_suburban(text_lower, result.get('province', ''))
            result.update(area_result)
            return result

        # Phân loại theo mã bưu chính
        postal_result = self._classify_by_postal_code(text)
        if postal_result['confidence'] > 0:
            result.update(postal_result)
            # Phân loại NỘI Ô / NGOẠI Ô
            area_result = self._classify_urban_suburban(text, result.get('province', ''))
            result.update(area_result)
            return result

        return result

    def _normalize_text(self, text: str) -> str:
        """Chuẩn hóa text để so sánh"""
        # Chuyển về lowercase
        text = text.lower()

        # Loại bỏ dấu tiếng Việt (giữ nguyên cho độ chính xác)
        # Có thể thêm logic loại bỏ dấu nếu cần

        # Loại bỏ ký tự đặc biệt thừa
        text = re.sub(r'\s+', ' ', text)

        return text.strip()

    def _classify_by_province(self, text: str) -> dict:
        """Phân loại theo tỉnh/thành phố"""
        result = {
            'region': 'unknown',
            'region_name': 'Không xác định',
            'confidence': 0.0,
            'province': '',
            'matched_keywords': []
        }

        if 'provinces' not in self.region_data:
            return result

        max_confidence = 0
        best_match = None
        matched_province = ''

        for region_key, region_info in self.region_data['provinces'].items():
            for province in region_info['provinces']:
                province_lower = province.lower()

                # Kiểm tra exact match hoặc partial match
                if province_lower in text or text.find(province_lower) != -1:
                    confidence = 0.9  # High confidence cho exact match

                    # Tính confidence dựa trên độ dài match
                    match_ratio = len(province_lower) / len(text)
                    confidence = min(confidence + match_ratio * 0.1, 1.0)

                    if confidence > max_confidence:
                        max_confidence = confidence
                        best_match = region_key
                        matched_province = province

        if best_match:
            region_info = self.region_data['provinces'][best_match]
            result.update({
                'region': best_match,
                'region_name': region_info['name'],
                'confidence': round(max_confidence, 2),
                'province': matched_province,
                'matched_keywords': [matched_province]
            })

        return result

    def _classify_by_keywords(self, text: str) -> dict:
        """Phân loại theo keywords đặc trưng"""
        result = {
            'region': 'unknown',
            'region_name': 'Không xác định',
            'confidence': 0.0,
            'province': '',
            'matched_keywords': []
        }

        if 'keywords' not in self.region_data:
            return result

        scores = {
            'north': 0,
            'central': 0,
            'south': 0
        }

        matched_keywords = []

        # Đếm số keyword match
        for region, keywords in self.region_data['keywords'].items():
            for keyword in keywords:
                if keyword in text:
                    scores[region] += 1
                    matched_keywords.append(keyword)

        # Tìm region có score cao nhất
        if max(scores.values()) > 0:
            best_region = max(scores, key=scores.get)
            confidence = scores[best_region] / sum(scores.values())

            # Map region key
            region_map = {
                'north': 'mien_bac',
                'central': 'mien_trung',
                'south': 'mien_nam'
            }

            region_key = region_map[best_region]
            region_info = self.region_data['provinces'][region_key]

            result.update({
                'region': region_key,
                'region_name': region_info['name'],
                'confidence': round(confidence, 2),
                'matched_keywords': matched_keywords
            })

        return result

    def _classify_by_postal_code(self, text: str) -> dict:
        """Phân loại theo mã bưu chính"""
        result = {
            'region': 'unknown',
            'region_name': 'Không xác định',
            'confidence': 0.0,
            'province': '',
            'matched_keywords': []
        }

        if 'postal_codes' not in self.region_data:
            return result

        # Tìm mã bưu chính trong text
        postal_pattern = r'\b\d{2}\d*\b'
        matches = re.findall(postal_pattern, text)

        if not matches:
            return result

        for postal_code in matches:
            prefix = postal_code[:2]

            # Kiểm tra prefix thuộc khu vực nào
            for region_key, prefixes in self.region_data['postal_codes'].items():
                if prefix in prefixes:
                    region_map = {
                        'mien_bac': 'mien_bac',
                        'mien_trung': 'mien_trung',
                        'mien_nam': 'mien_nam'
                    }

                    region_info = self.region_data['provinces'][region_key]

                    result.update({
                        'region': region_key,
                        'region_name': region_info['name'],
                        'confidence': 0.7,  # Medium confidence cho postal code
                        'matched_keywords': [f'Mã bưu chính: {postal_code}']
                    })
                    return result

        return result

    def _classify_urban_suburban(self, text: str, province: str = '') -> dict:
        """
        Phân loại NỘI Ô / NGOẠI Ô dựa trên địa chỉ

        Logic đơn giản:
        - NỘI Ô = Thành phố Hồ Chí Minh
        - NGOẠI Ô = Tất cả các tỉnh/thành khác

        Args:
            text: Text đã normalize (lowercase)
            province: Tỉnh/Thành phố đã được xác định

        Returns:
            dict: {'area_type': 'noi_o'/'ngoai_o', 'area_name': str}
        """
        result = {
            'area_type': 'unknown',
            'area_name': 'Không xác định'
        }

        # Kiểm tra Thành phố Hồ Chí Minh
        hcm_keywords = [
            'hồ chí minh',
            'tp hồ chí minh',
            'tp. hồ chí minh',
            'thành phố hồ chí minh',
            'sài gòn',
            'saigon',
            'tp hcm',
            'tp. hcm',
            'hcm'
        ]

        # Kiểm tra trong text hoặc province
        text_to_check = (text + ' ' + province.lower()).lower()

        for keyword in hcm_keywords:
            if keyword in text_to_check:
                result['area_type'] = 'noi_o'
                result['area_name'] = 'NỘI Ô'
                return result

        # Nếu không phải HCM và đã xác định được tỉnh → NGOẠI Ô
        if province and province.strip():
            result['area_type'] = 'ngoai_o'
            result['area_name'] = 'NGOẠI Ô'

        return result

    def get_region_info(self, region_key: str) -> dict:
        """
        Lấy thông tin chi tiết về một khu vực

        Args:
            region_key: Key của khu vực (mien_bac/mien_trung/mien_nam)

        Returns:
            dict: Thông tin khu vực
        """
        if 'provinces' not in self.region_data:
            return {}

        return self.region_data['provinces'].get(region_key, {})

    def get_all_regions(self) -> list:
        """Lấy danh sách tất cả các khu vực"""
        if 'provinces' not in self.region_data:
            return []

        regions = []
        for key, info in self.region_data['provinces'].items():
            regions.append({
                'key': key,
                'name': info['name'],
                'code': info['code'],
                'province_count': len(info['provinces'])
            })

        return regions

    def get_provinces_by_region(self, region_key: str) -> list:
        """Lấy danh sách tỉnh/thành theo khu vực"""
        region_info = self.get_region_info(region_key)
        return region_info.get('provinces', [])


if __name__ == "__main__":
    # Test
    classifier = RegionClassifier()

    # Test với một số địa chỉ mẫu
    test_cases = [
        "Số 1 Đại Cồ Việt, Hai Bà Trưng, Hà Nội",
        "123 Lê Lợi, Quận 1, TP. Hồ Chí Minh",
        "456 Trần Phú, Hải Châu, Đà Nẵng"
    ]

    for address in test_cases:
        result = classifier.classify(address)
        print(f"\nĐịa chỉ: {address}")
        print(f"Khu vực: {result['region_name']}")
        print(f"Độ tin cậy: {result['confidence']}")
