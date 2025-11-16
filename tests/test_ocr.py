"""
Test cases cho module OCR
"""
import unittest
import sys
from pathlib import Path

# Thêm thư mục src vào path
sys.path.append(str(Path(__file__).parent.parent))

from src.region_classifier import RegionClassifier


class TestRegionClassifier(unittest.TestCase):
    """Test cases cho RegionClassifier"""
    
    def setUp(self):
        """Setup trước mỗi test"""
        self.classifier = RegionClassifier()
    
    def test_classify_hanoi(self):
        """Test phân loại địa chỉ Hà Nội"""
        text = "Số 1 Đại Cồ Việt, Hai Bà Trưng, Hà Nội"
        result = self.classifier.classify(text)
        
        self.assertEqual(result['region'], 'mien_bac')
        self.assertEqual(result['region_name'], 'Miền Bắc')
        self.assertGreater(result['confidence'], 0)
    
    def test_classify_hochiminh(self):
        """Test phân loại địa chỉ TP.HCM"""
        text = "123 Nguyễn Huệ, Quận 1, TP. Hồ Chí Minh"
        result = self.classifier.classify(text)
        
        self.assertEqual(result['region'], 'mien_nam')
        self.assertEqual(result['region_name'], 'Miền Nam')
        self.assertGreater(result['confidence'], 0)
    
    def test_classify_danang(self):
        """Test phân loại địa chỉ Đà Nẵng"""
        text = "456 Trần Phú, Hải Châu, Đà Nẵng"
        result = self.classifier.classify(text)
        
        self.assertEqual(result['region'], 'mien_trung')
        self.assertEqual(result['region_name'], 'Miền Trung')
        self.assertGreater(result['confidence'], 0)
    
    def test_classify_empty_text(self):
        """Test với text rỗng"""
        result = self.classifier.classify("")
        
        self.assertEqual(result['region'], 'unknown')
        self.assertEqual(result['confidence'], 0)
    
    def test_get_all_regions(self):
        """Test lấy danh sách khu vực"""
        regions = self.classifier.get_all_regions()
        
        self.assertEqual(len(regions), 3)
        region_names = [r['name'] for r in regions]
        self.assertIn('Miền Bắc', region_names)
        self.assertIn('Miền Trung', region_names)
        self.assertIn('Miền Nam', region_names)
    
    def test_get_provinces_by_region(self):
        """Test lấy danh sách tỉnh theo khu vực"""
        provinces = self.classifier.get_provinces_by_region('mien_bac')
        
        self.assertIsInstance(provinces, list)
        self.assertGreater(len(provinces), 0)
        self.assertIn('Hà Nội', provinces)


class TestImageProcessor(unittest.TestCase):
    """Test cases cho ImageProcessor"""
    
    def setUp(self):
        """Setup trước mỗi test"""
        try:
            from src.image_processor import ImageProcessor
            self.processor = ImageProcessor()
        except ImportError:
            self.skipTest("ImageProcessor requires OpenCV")
    
    def test_processor_initialization(self):
        """Test khởi tạo ImageProcessor"""
        self.assertIsNotNone(self.processor)


def run_tests():
    """Chạy tất cả tests"""
    # Tạo test suite
    suite = unittest.TestLoader().loadTestsFromModule(sys.modules[__name__])
    
    # Chạy tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Trả về kết quả
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
