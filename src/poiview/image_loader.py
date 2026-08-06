from pathlib import Path

import rawpy

from PySide6.QtGui import QImage, QPixmap
from PIL import Image, ImageOps


class ImageLoader:

    RAW_EXTENSIONS = {
        ".cr2",
        ".cr3",
        ".nef",
        ".arw",
        ".dng",
        ".rw2",
    }

    @staticmethod
    def load(path: str | Path) -> QPixmap:
        path = Path(path)

        if path.suffix.lower() in ImageLoader.RAW_EXTENSIONS:
            return ImageLoader._load_raw(path)

        image = Image.open(path)
        image = ImageOps.exif_transpose(image)

        if image.mode != "RGB":
            image = image.convert("RGB")

        data = image.tobytes()

        qimage = QImage(
            data,
            image.width,
            image.height,
            image.width * 3,
            QImage.Format_RGB888,
        ).copy()

        return QPixmap.fromImage(qimage)

    @staticmethod
    def _load_raw(path: Path) -> QPixmap:

        with rawpy.imread(str(path)) as raw:
            rgb = raw.postprocess()

        h, w, c = rgb.shape

        image = QImage(
            rgb.data,
            w,
            h,
            c * w,
            QImage.Format_RGB888,
        ).copy()

        return QPixmap.fromImage(image)