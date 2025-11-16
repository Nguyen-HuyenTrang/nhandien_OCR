"""
Module xử lý ảnh trước khi OCR
"""
import cv2
import numpy as np
from PIL import Image
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ImageProcessor:
    """Xử lý ảnh để tăng độ chính xác của OCR"""

    def __init__(self):
        self.logger = logger

    def preprocess_image(self, image_path: str, method: str = 'minimal') -> np.ndarray:
        """
        Tiền xử lý ảnh trước khi OCR

        Args:
            image_path: Đường dẫn đến ảnh hoặc numpy array của ảnh
            method: Phương pháp xử lý:
                - 'minimal': Giữ nguyên ảnh gốc, chỉ resize nếu cần (KHUYẾN NGHỊ)
                - 'auto': Tăng contrast và độ sắc nét
                - 'grayscale': Chuyển sang ảnh xám
                - 'threshold': Nhị phân hóa (chỉ dùng khi ảnh rất rõ nét)
                - 'denoise': Giảm nhiễu

        Returns:
            np.ndarray: Ảnh đã được xử lý
        """
        try:
            # Đọc ảnh nếu là đường dẫn, hoặc dùng trực tiếp nếu là numpy array
            if isinstance(image_path, str):
                image = cv2.imread(image_path)
                if image is None:
                    raise ValueError(f"Không thể đọc ảnh từ {image_path}")
            else:
                # Đã là numpy array
                image = image_path

            self.logger.info(f"Đọc ảnh thành công: {image_path}")

            if method == 'minimal':
                # Chỉ resize nếu ảnh quá lớn, giữ nguyên màu sắc
                processed = self._minimal_process(image)
            elif method == 'auto':
                # Tự động xử lý với tăng contrast
                processed = self._auto_process(image)
            elif method == 'grayscale':
                processed = self._convert_to_grayscale(image)
            elif method == 'threshold':
                processed = self._apply_threshold(image)
            elif method == 'denoise':
                processed = self._denoise(image)
            else:
                processed = image

            return processed

        except Exception as e:
            self.logger.error(f"Lỗi xử lý ảnh: {e}")
            raise

    def _auto_process(self, image: np.ndarray) -> np.ndarray:
        """Tự động xử lý ảnh với pipeline tối ưu cho nhãn bưu kiện"""
        # Với nhãn bưu kiện, giữ ảnh gốc càng nhiều càng tốt

        # Resize nếu ảnh quá lớn (giúp OCR nhanh hơn)
        height, width = image.shape[:2]
        if width > 2000 or height > 2000:
            scale = min(2000/width, 2000/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            image = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            self.logger.info(f"Resize ảnh từ {width}x{height} xuống {new_width}x{new_height}")

        # Tăng độ sắc nét nhẹ
        kernel_sharpening = np.array([[-1,-1,-1],
                                      [-1, 9,-1],
                                      [-1,-1,-1]])
        sharpened = cv2.filter2D(image, -1, kernel_sharpening)

        # Tăng contrast nhẹ bằng CLAHE (áp dụng cho từng channel nếu ảnh màu)
        if len(image.shape) == 3:
            # Chuyển sang LAB color space
            lab = cv2.cvtColor(sharpened, cv2.COLOR_BGR2LAB)
            l, a, b = cv2.split(lab)

            # Áp dụng CLAHE cho channel L
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            l = clahe.apply(l)

            # Merge và chuyển về BGR
            enhanced_lab = cv2.merge([l, a, b])
            enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)
        else:
            # Ảnh grayscale
            clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(sharpened)

        return enhanced

    def _minimal_process(self, image: np.ndarray) -> np.ndarray:
        """Xử lý tối thiểu - chỉ resize nếu cần"""
        height, width = image.shape[:2]

        # Chỉ resize nếu ảnh quá lớn (tốn tài nguyên) hoặc quá nhỏ (mất thông tin)
        if width > 3000 or height > 3000:
            scale = min(3000/width, 3000/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_AREA)
            self.logger.info(f"Resize ảnh từ {width}x{height} xuống {new_width}x{new_height}")
            return resized
        elif width < 800 and height < 800:
            # Upscale ảnh nhỏ
            scale = min(1200/width, 1200/height)
            new_width = int(width * scale)
            new_height = int(height * scale)
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            self.logger.info(f"Upscale ảnh từ {width}x{height} lên {new_width}x{new_height}")
            return resized

        # Ảnh có kích thước vừa phải, giữ nguyên
        return image

    def _convert_to_grayscale(self, image: np.ndarray) -> np.ndarray:
        """Chuyển ảnh sang grayscale"""
        if len(image.shape) == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image

    def _apply_threshold(self, image: np.ndarray) -> np.ndarray:
        """Áp dụng threshold để làm rõ text"""
        gray = self._convert_to_grayscale(image)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return thresh

    def _denoise(self, image: np.ndarray) -> np.ndarray:
        """Giảm nhiễu trong ảnh"""
        if len(image.shape) == 3:
            return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        else:
            return cv2.fastNlMeansDenoising(image, None, 10, 7, 21)

    def resize_image(self, image: np.ndarray, max_width: int = 1920,
                     max_height: int = 1080) -> np.ndarray:
        """
        Resize ảnh nếu quá lớn

        Args:
            image: Ảnh cần resize
            max_width: Chiều rộng tối đa
            max_height: Chiều cao tối đa

        Returns:
            np.ndarray: Ảnh đã được resize
        """
        height, width = image.shape[:2]

        if width <= max_width and height <= max_height:
            return image

        # Tính tỷ lệ resize
        ratio = min(max_width / width, max_height / height)
        new_width = int(width * ratio)
        new_height = int(height * ratio)

        resized = cv2.resize(image, (new_width, new_height),
                           interpolation=cv2.INTER_AREA)

        self.logger.info(f"Resize ảnh từ {width}x{height} xuống {new_width}x{new_height}")
        return resized

    def rotate_image(self, image: np.ndarray, angle: float) -> np.ndarray:
        """
        Xoay ảnh theo góc cho trước

        Args:
            image: Ảnh cần xoay
            angle: Góc xoay (độ)

        Returns:
            np.ndarray: Ảnh đã được xoay
        """
        height, width = image.shape[:2]
        center = (width // 2, height // 2)

        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(image, rotation_matrix, (width, height),
                                flags=cv2.INTER_CUBIC,
                                borderMode=cv2.BORDER_REPLICATE)

        return rotated

    def detect_and_correct_skew(self, image: np.ndarray) -> np.ndarray:
        """
        Phát hiện và sửa độ nghiêng của ảnh

        Args:
            image: Ảnh cần sửa

        Returns:
            np.ndarray: Ảnh đã được sửa nghiêng
        """
        try:
            # Chuyển sang grayscale
            gray = self._convert_to_grayscale(image)

            # Áp dụng threshold
            _, binary = cv2.threshold(gray, 0, 255,
                                    cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)

            # Tìm các điểm không phải background
            coords = np.column_stack(np.where(binary > 0))

            # Tính góc nghiêng
            angle = cv2.minAreaRect(coords)[-1]

            # Điều chỉnh góc
            if angle < -45:
                angle = 90 + angle
            elif angle > 45:
                angle = angle - 90

            # Xoay ảnh nếu góc nghiêng đáng kể
            if abs(angle) > 0.5:
                self.logger.info(f"Sửa độ nghiêng: {angle:.2f} độ")
                return self.rotate_image(image, angle)

            return image

        except Exception as e:
            self.logger.warning(f"Không thể sửa độ nghiêng: {e}")
            return image

    def crop_border(self, image: np.ndarray, border_size: int = 10) -> np.ndarray:
        """
        Cắt bỏ viền ảnh

        Args:
            image: Ảnh cần cắt
            border_size: Kích thước viền cần cắt (pixels)

        Returns:
            np.ndarray: Ảnh đã được cắt viền
        """
        height, width = image.shape[:2]

        if height <= 2 * border_size or width <= 2 * border_size:
            return image

        return image[border_size:height-border_size,
                    border_size:width-border_size]

    def save_processed_image(self, image: np.ndarray, output_path: str) -> None:
        """
        Lưu ảnh đã xử lý

        Args:
            image: Ảnh cần lưu
            output_path: Đường dẫn lưu ảnh
        """
        try:
            cv2.imwrite(output_path, image)
            self.logger.info(f"Đã lưu ảnh xử lý tại: {output_path}")
        except Exception as e:
            self.logger.error(f"Lỗi khi lưu ảnh: {e}")
            raise


if __name__ == "__main__":
    # Test
    processor = ImageProcessor()
    print("ImageProcessor module loaded successfully!")
