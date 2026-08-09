from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QPushButton,
    QHBoxLayout,
    QVBoxLayout,
    QLabel,
)
from poiview.seek_slider import SeekSlider


class Overlay(QWidget):

    previousClicked = Signal()
    nextClicked = Signal()
    favouriteClicked = Signal()
    trashClicked = Signal()
    fullscreenClicked = Signal()
    hideClicked = Signal()
    infoClicked = Signal()
    helpClicked = Signal()
    playPauseClicked = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setAttribute(Qt.WA_StyledBackground, False)
        self.setStyleSheet("background: transparent;")

        self.previous_button = QPushButton("←")
        self.next_button = QPushButton("→")
        self.play_button = QPushButton("▶")
        self.seek_slider = SeekSlider(Qt.Horizontal)
        self.seek_slider.setMinimumHeight(30)
        self.seek_slider.setFocusPolicy(Qt.NoFocus)
        self.time_label = QLabel("00:00 / 00:00")
        
        self.position_label = QLabel("0 / 0")
        self.position_label.setStyleSheet("font-size: 18px; color: white;")

        self.cache_label = QLabel("(-0 / +0)")
        self.cache_label.setStyleSheet("font-size: 16px; color: white;")
        
        self.favourite_button = QPushButton("♡")
        self.trash_button = QPushButton("🗑")
        self.fullscreen_button = QPushButton("⛶")
        self.hide_button = QPushButton("✕")
        self.info_button = QPushButton("ⓘ")
        self.help_button = QPushButton("?")

        for button in (
            self.previous_button,
            self.next_button,
            self.favourite_button,
            self.trash_button,
            self.fullscreen_button,
            self.hide_button,
            self.info_button,
            self.help_button,
            self.play_button,
        ):
            button.setFixedSize(56, 56)
            button.setFocusPolicy(Qt.NoFocus)
            button.setStyleSheet("""
                QPushButton {
                    background: rgba(20,20,20,90);
                    color: white;
                    border-radius: 28px;
                    font-size:24px;
                }

                QPushButton:hover {
                    background: rgba(60,60,60,150);
                }
            """)

        self.previous_button.clicked.connect(self.previousClicked)
        self.next_button.clicked.connect(self.nextClicked)
        self.favourite_button.clicked.connect(self.favouriteClicked)
        self.trash_button.clicked.connect(self.trashClicked)
        self.fullscreen_button.clicked.connect(self.fullscreenClicked)
        self.hide_button.clicked.connect(self.hideClicked)
        self.info_button.clicked.connect(self.infoClicked)
        self.help_button.clicked.connect(self.helpClicked)
        self.play_button.clicked.connect(self.playPauseClicked)

        layout = QVBoxLayout(self)

        layout.addWidget(self.position_label)
        layout.addWidget(self.cache_label)
        layout.addStretch()

        controls = QVBoxLayout()
        controls.addWidget(self.time_label)
        controls.addWidget(self.seek_slider)

        bottom = QHBoxLayout()

        bottom.addWidget(self.previous_button)
        bottom.addStretch()
        bottom.addWidget(self.favourite_button)
        bottom.addWidget(self.trash_button)
        bottom.addWidget(self.play_button)
        bottom.addWidget(self.fullscreen_button)
        bottom.addWidget(self.info_button)
        bottom.addWidget(self.help_button)
        bottom.addWidget(self.hide_button)
        
        bottom.addStretch()
        bottom.addWidget(self.next_button)
        layout.addLayout(controls)
        layout.addLayout(bottom)
        
        self.hide_video_controls()
        
    def set_position_info(self, current, total, before, after):
        self.position_label.setText(
            f"{current} / {total}"
        )

        self.cache_label.setText(
            f"(-{before} / +{after})"
        )
    
    def set_favourite(self, favourite: bool):
        if favourite:
            self.favourite_button.setText("♥")
        else:
            self.favourite_button.setText("♡")
    
    def set_playing(self, playing: bool):
        if playing:
            self.play_button.setText("⏸")
        else:
            self.play_button.setText("▶")

    def show_video_controls(self):
        self.time_label.show()
        self.seek_slider.show()
        self.play_button.show()


    def hide_video_controls(self):
        self.time_label.hide()
        self.seek_slider.hide()
        self.play_button.hide()
    
    def mousePressEvent(self, event):
        super().mousePressEvent(event)