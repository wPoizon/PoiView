from PySide6.QtCore import Qt
from PySide6.QtWidgets import QSlider


class SeekSlider(QSlider):

    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:

            value = self.minimum() + (
                (self.maximum() - self.minimum())
                * event.position().x()
                / self.width()
            )

            self.setValue(int(value))
            self.sliderMoved.emit(int(value))

        super().mousePressEvent(event)