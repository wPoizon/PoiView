import sys
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
)


SUPPORTED = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".gif",
    ".webp",
    ".cr2",
    ".dng",
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
}


class Viewer(QMainWindow):

    def __init__(self, folder):
        super().__init__()

        self.files = sorted(
            f for f in Path(folder).iterdir()
            if f.suffix.lower() in SUPPORTED
        )

        self.index = 0

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)

        self.setCentralWidget(self.label)

        self.showFullScreen()

        self.show_current()

    def show_current(self):

        if not self.files:
            self.label.setText("No files found")
            return

        file = self.files[self.index]

        if file.suffix.lower() in {
            ".jpg",
            ".jpeg",
            ".png",
            ".bmp",
            ".gif",
            ".webp",
        }:

            pix = QPixmap(str(file))

            self.label.setPixmap(
                pix.scaled(
                    self.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )

        else:

            self.label.setText(file.name)

        self.setWindowTitle(file.name)

    def resizeEvent(self, event):
        self.show_current()

    def keyPressEvent(self, event):

        if event.key() == Qt.Key_Right:

            if self.index < len(self.files) - 1:
                self.index += 1
                self.show_current()

        elif event.key() == Qt.Key_Left:

            if self.index > 0:
                self.index -= 1
                self.show_current()

        elif event.key() == Qt.Key_Escape:

            self.close()


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage:")
        print("python main.py /path/to/folder")
        sys.exit()

    app = QApplication(sys.argv)

    window = Viewer(sys.argv[1])

    window.show()

    sys.exit(app.exec())