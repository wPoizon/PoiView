from PySide6.QtWidgets import QApplication, QFileDialog
import sys

from poiview.viewer import Viewer


def main():
    app = QApplication(sys.argv)

    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.ExistingFile)
        dialog.setNameFilter(
            "Media files (*.jpg *.jpeg *.png *.bmp *.gif *.webp "
            "*.cr2 *.dng *.mp4 *.mov *.avi *.mkv)"
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