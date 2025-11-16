"""
Khởi tạo package src
"""
from .ocr_engine import OCREngine
from .region_classifier import RegionClassifier
from .image_processor import ImageProcessor

__all__ = ['OCREngine', 'RegionClassifier', 'ImageProcessor']
__version__ = '1.0.0'
