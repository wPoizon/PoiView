from PySide6.QtWidgets import QApplication, QFileDialog
import sys

from poiview.viewer import Viewer


def main():
    app = QApplication(sys.argv)

    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        path = QFileDialog.getExistingDirectory(
            None,
            "Open folder",
        )

        if not path:
            sys.exit()

    window = Viewer(path)
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()