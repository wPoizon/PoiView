from PySide6.QtWidgets import QApplication
import sys

from poiview.viewer import Viewer


def main():
    app = QApplication(sys.argv)

    window = Viewer("/home/william/Desktop/norge/sorted")
    window.showMaximized()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()