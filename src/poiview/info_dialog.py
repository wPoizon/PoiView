from pathlib import Path
import json
import subprocess

from PySide6.QtWidgets import (
    QDialog,
    QFormLayout,
    QLabel,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)


class InfoDialog(QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("File information")
        self.resize(700, 600)

        self.form = QFormLayout()

        container = QWidget()
        container.setLayout(self.form)

        scroll = QScrollArea()
        scroll.setWidget(container)
        scroll.setWidgetResizable(True)

        layout = QVBoxLayout(self)
        layout.addWidget(scroll)

    def set_file(self, path):

        while self.form.rowCount():
            self.form.removeRow(0)

        path = Path(path)
        self._section("File")
        
        self._add("Filename", path.name)
        self._add("Folder", str(path.parent))
        self._add("Extension", path.suffix)
        self._add(
            "Size",
            self._format_size(path.stat().st_size),
        )

        try:
            result = subprocess.run(
                [
                    "exiftool",
                    "-j",
                    str(path),
                ],
                capture_output=True,
                text=True,
                check=True,
            )

            metadata = json.loads(result.stdout)[0]
            if "CreateDate" in metadata:
                metadata["CreateDate"] = (
                    metadata["CreateDate"]
                    .replace(":", "-", 2)
                )

        except Exception as e:
            print(e)
            return

        width = metadata.get("ImageWidth")
        height = metadata.get("ImageHeight")

        if width and height:
            self._add("Resolution", f"{width} × {height}")

        wanted = [
            # Video
            ("Duration", "Duration"),
            ("VideoFrameRate", "FPS"),
            ("CompressorName", "Codec"),
            ("VideoCodec", "Codec"),
            ("CodecID", "Codec"),
            ("AvgBitrate", "Bitrate"),
            ("AudioCodec", "Audio codec"),

            # Camera
            ("Make", "Camera make"),
            ("Model", "Camera model"),
            ("LensModel", "Lens"),
            ("ISO", "ISO"),
            ("FNumber", "Aperture"),
            ("ExposureTime", "Exposure"),
            ("FocalLength", "Focal length"),

            # Date
            ("CreateDate", "Taken"),

            # GPS
            ("GPSLatitude", "Latitude"),
            ("GPSLongitude", "Longitude"),
        ]

        for exif_name, label in wanted:

            if exif_name in metadata:
                self._add(label, metadata[exif_name])
                
    def _format_size(self, size):

        units = ["B", "KB", "MB", "GB", "TB"]

        size = float(size)

        for unit in units:

            if size < 1024 or unit == units[-1]:
                return f"{size:.1f} {unit}"

            size /= 1024

    def _section(self, title):

        label = QLabel(f"<b>{title}</b>")
        label.setStyleSheet("font-size: 15px; padding-top: 8px;")

        self.form.addRow(label)
        
    def _add_if_exists(self, metadata, key, label):

        value = metadata.get(key)

        if value is not None:
            self._add(label, value)

    def _add(self, name, value):
        self.form.addRow(name, QLabel(str(value)))