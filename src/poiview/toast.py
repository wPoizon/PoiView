from PySide6.QtCore import Qt, QTimer, QPropertyAnimation
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

        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.animation.setDuration(180)
        self.small = False
        
    def set_small(self):
        self.setStyleSheet("""
            QLabel {
                background: rgba(20,20,20,160);
                color: white;
                border-radius: 8px;
                padding: 6px 12px;
                font-size: 14px;
            }
        """)

    def show_message(self, text: str, duration: int = 2000):
        self.timer.stop()
        self.animation.stop()

        self.setText(text)
        self.adjustSize()

        if self.parent():
            x = (self.parent().width() - self.width()) // 2
            margin = 20
            y = margin
            self.move(x, y)

        self.setWindowOpacity(0.0)
        self.raise_()
        self.show()

        self.animation.setStartValue(0.0)
        self.animation.setEndValue(1.0)
        self.animation.start()

        self.timer.start(duration)