from PySide6.QtCore import Qt, QTimer
from PySide6.QtWidgets import QLabel


class Toast(QLabel):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.hide()

        self.setAlignment(Qt.AlignCenter)

        self.setStyleSheet("""
            QLabel {
                background: rgba(20,20,20,180);
                color: white;
                border-radius: 12px;
                padding: 10px 18px;
                font-size: 18px;
            }
        """)

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.hide)

    def show_message(self, text: str, duration: int = 2000):
        self.setText(text)
        self.adjustSize()

        if self.parent():
            x = (self.parent().width() - self.width()) // 2
            margin = 20
            y = margin
            self.move(x, y)

        self.raise_()
        self.show()

        self.timer.start(duration)