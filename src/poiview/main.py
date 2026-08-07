from PySide6.QtWidgets import QApplication, QFileDialog
import sys

from poiview.viewer import Viewer


def main():
    app = QApplication(sys.argv)

    if len(sys.argv) > 1:
        path = sys.argv[1]
    else:
        dialog = QFileDialog()
        dialog.setFileMode(QFileDialog.AnyFile)
        dialog.setOption(QFileDialog.ShowDirsOnly, False)

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