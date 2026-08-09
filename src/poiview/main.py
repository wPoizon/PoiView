from pathlib import Path
import sys

from PySide6.QtWidgets import QApplication, QFileDialog

from poiview.viewer import Viewer
from poiview.media import SUPPORTED_EXTENSIONS


def main():
    app = QApplication(sys.argv)

    if len(sys.argv) > 1:
        path = sys.argv[1]
        file = Path(path)

        if not file.exists():
            print(f"File not found: {path}")
            sys.exit(1)

        if file.is_file() and file.suffix.lower() not in SUPPORTED_EXTENSIONS:
            print(f"Unsupported file type: {file.suffix}")
            sys.exit(1)
    else:
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter(
            "Media files (*.jpg *.jpeg *.png *.bmp *.gif *.webp "
            "*.cr2 *.cr3 *.nef *.arw *.dng *.rw2 "
            "*.mp4 *.mov *.avi *.mkv)"
        )

        if dialog.exec():
            selected = dialog.selectedFiles()[0]
            path = selected
        else:
            sys.exit()

        if not path:
            sys.exit()

    viewer = Viewer(path)
    viewer.showMaximized()

    viewer.setFocus()
    viewer.activateWindow()
    viewer.raise_()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()