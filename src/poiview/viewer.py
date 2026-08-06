from PySide6.QtCore import Qt, QTimer, QEvent
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
)

from poiview.media import MediaFolder
from poiview.cache import ImageCache
from poiview.image_loader import ImageLoader
from poiview.video_loader import VideoLoader
from poiview.overlay import Overlay
from poiview.toast import Toast
from poiview.info_dialog import InfoDialog

from pathlib import Path
import shutil


class Viewer(QMainWindow):
    
    def __init__(self, folder, cache_amount=10):
        super().__init__()
        
        self.cache_amount = cache_amount
        
        self.media = MediaFolder(folder)
        self.cache = ImageCache(max_items=cache_amount * 2 + 1)
        self.video = VideoLoader()
        
        self.favourites_folder = Path(folder) / "favourites"
        self.favourites_folder.mkdir(exist_ok=True)
        
        self.trash_folder = Path(folder) / "trash"
        self.trash_folder.mkdir(exist_ok=True)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        
        self.raw_label = QLabel("RAW", self)
        self.raw_label.setStyleSheet("""
            QLabel {
                background-color: rgba(0, 0, 0, 180);
                color: white;
                font-weight: bold;
                padding: 4px 8px;
                border-radius: 6px;
            }
        """)
        self.raw_label.hide()
        self.raw_label.raise_()
        
        self.overlay = Overlay(self)
        self.toast = Toast(self)
        self.info_dialog = InfoDialog(self)
        self.last_action = None
        
        self.setMouseTracking(True)

        self.cursor_timer = QTimer(self)
        self.cursor_timer.setSingleShot(True)
        self.cursor_timer.timeout.connect(self.hide_cursor)

        self.cursor_timer.start(1000)

        self.overlay.previousClicked.connect(self.previous)
        self.overlay.nextClicked.connect(self.next)
        self.overlay.favouriteClicked.connect(self.favourite)
        self.overlay.trashClicked.connect(self.trash)
        self.overlay.hideClicked.connect(self.hide_overlay)
        self.overlay.fullscreenClicked.connect(self.toggle_fullscreen)
        self.overlay.infoClicked.connect(self.show_info)
        self.overlay.helpClicked.connect(self.show_help)
        self.video.playbackStateChanged.connect(
            lambda _:
                self.overlay.set_playing(
                    self.video.is_playing()
                )
        )

        self.video.positionChanged.connect(
            self.update_video_time
        )

        self.video.durationChanged.connect(
            self.update_video_time
        )

        self.overlay.playPauseClicked.connect(self.video.toggle_pause)
        self.overlay.seek_slider.sliderMoved.connect(
            self.video.seek
        )

        self.stack = QStackedWidget()

        self.stack.addWidget(self.label)
        self.stack.addWidget(self.video.widget)

        self.setCentralWidget(self.stack)
        self.setMouseTracking(True)
        self.stack.setMouseTracking(True)
        self.label.setMouseTracking(True)
        self.video.widget.setMouseTracking(True)
        self.overlay.setGeometry(self.rect())
        self.overlay.show()
        self.overlay.raise_()

        self.update_view()
        self.video.resize(self.stack.size())
        self.overlay_hidden = False
        
        QApplication.instance().installEventFilter(self)


    def update_view(self):
        current = self.media.current()
        
        self.overlay.set_favourite(
            (self.favourites_folder / current.name).exists()
        )
        
        if current.suffix.lower() in ImageLoader.RAW_EXTENSIONS:
            self.raw_label.show()
        else:
            self.raw_label.hide()
        
        before = self.media.files[
            max(0, self.media.index - self.cache_amount):self.media.index
        ]

        after = self.media.files[
            self.media.index + 1:
            min(self.media.count(), self.media.index + self.cache_amount+1)
        ]

        self.cache.preload(before + after)
        
        if self.video.is_video(current):
            self.overlay.show_video_controls()
            self.stack.setCurrentWidget(self.video.widget)
            self.video.load(current)

        else:

            self.video.stop()
            self.overlay.hide_video_controls()

            self.stack.setCurrentWidget(self.label)

            pixmap = self.cache.get(current)

            self.label.setPixmap(
                pixmap.scaled(
                    self.label.size(),
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation,
                )
            )
        self.overlay.raise_()
        self.raw_label.raise_()
        
        if self.info_dialog.isVisible():
            self.info_dialog.set_file(current)

    def format_time(self, milliseconds):

        seconds = milliseconds // 1000

        minutes = seconds // 60
        seconds %= 60

        return f"{minutes:02}:{seconds:02}"
    
    def update_video_time(self):

        position = self.video.position()
        duration = self.video.duration()

        self.overlay.time_label.setText(
            f"{self.format_time(position)} / "
            f"{self.format_time(duration)}"
        )

        self.overlay.seek_slider.setMaximum(duration)
        self.overlay.seek_slider.setValue(position)
        
    def show_overlay(self):
        self.overlay_hidden = False
        self.overlay.show()
        self.overlay.raise_()


    def hide_overlay(self):
        self.overlay_hidden = True
        self.overlay.hide()
        
    def hide_cursor(self):
        self.setCursor(Qt.BlankCursor)

        if not self.overlay_hidden:
            self.overlay.hide()


    def show_cursor(self):
        self.unsetCursor()
        self.cursor_timer.start(1000)
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.setWindowState(
                (self.windowState() & ~Qt.WindowFullScreen)
                | Qt.WindowMaximized
            )
        else:
            self.setWindowState(
                self.windowState() | Qt.WindowFullScreen
            )


    def mouseDoubleClickEvent(self, event):
        self.toggle_fullscreen()
        super().mouseDoubleClickEvent(event)
        
    def show_shortcuts(self):
        QMessageBox.information(
            self,
            "Keyboard shortcuts",
            """
← / →    Previous / Next
Enter    Favourite
F        Fullscreen
H        Toggle overlay
Esc      Exit fullscreen
""".strip(),
        )
    
    def show_info(self):

        current = self.media.current()

        if current is None:
            return

        self.info_dialog.set_file(current)
        self.info_dialog.show()
        self.info_dialog.raise_()
        self.info_dialog.activateWindow()
        
    def show_help(self):
        QMessageBox.information(
            self,
            "Keyboard shortcuts",
            """
← / →    Previous / Next media
Space    Play / Pause video
Enter    Favourite
Delete   Move to trash
Ctrl+Z   Undo
H         Toggle overlay
F         Toggle fullscreen
Esc       Exit fullscreen
I         File information
F1        Help
""".strip(),
        )

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Space:
            self.video.toggle_pause()
            return
        
        if event.key() == Qt.Key_H:
            if self.overlay_hidden:
                self.show_overlay()
            else:
                self.hide_overlay()
            return

        if event.key() == Qt.Key_F:
            self.toggle_fullscreen()
            return

        if event.key() == Qt.Key_Escape and self.isFullScreen():
            self.setWindowState(
                (self.windowState() & ~Qt.WindowFullScreen)
                | Qt.WindowMaximized
            )
            return

        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.favourite()
            return
        
        if event.key() == Qt.Key_Delete:
            self.trash()
            return
        
        if (
            event.key() == Qt.Key_Z
            and event.modifiers() & Qt.ControlModifier
        ):
            self.undo()
            return

        if event.key() == Qt.Key_F1:
            self.show_help()
            return

        if event.key() == Qt.Key_I:
            self.show_info()
            return
        
        if event.key() == Qt.Key_Right:
            self.next()

        elif event.key() == Qt.Key_Left:
            self.previous()
        
    
    def resizeEvent(self, event):
        self.overlay.setGeometry(self.rect())
        self.video.resize(self.stack.size())
        self.overlay.raise_()
        
        super().resizeEvent(event)
        
        margin = 12

        self.raw_label.adjustSize()
        self.raw_label.move(
            self.width() - self.raw_label.width() - margin,
            margin
        )

        current = self.media.current()

        if current is None:
            return

        if self.video.is_video(current):
            return

        pixmap = self.cache.get(current)

        self.label.setPixmap(
            pixmap.scaled(
                self.label.size(),
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )
    
    def previous(self):
        self.media.previous()
        self.update_view()


    def next(self):
        self.media.next()
        self.update_view()
    
    def favourite(self):
        current = self.media.current()

        if current is None:
            return
        
        destination = self.favourites_folder / current.name

        if destination.exists():
            destination.unlink()
            self.overlay.set_favourite(False)
            self.toast.show_message("🤍 Removed from favourites")
        else:
            shutil.copy2(current, destination)
            self.overlay.set_favourite(True)
            self.toast.show_message("❤️ Added to favourites")
            
    def trash(self):
        current = self.media.current()

        if current is None:
            return

        destination = self.trash_folder / current.name
        
        self.last_action = {
            "type": "trash",
            "source": current,
            "destination": destination,
            "index": self.media.index,
        }

        shutil.move(current, destination)

        self.media.files.pop(self.media.index)

        if not self.media.files:
            self.label.clear()
            self.video.stop()
            self.toast.show_message("🗑 Moved to trash")
            return

        if self.media.index >= len(self.media.files):
            self.media.index = len(self.media.files) - 1

        self.update_view()

        self.toast.show_message("🗑 Moved to trash")
        
    def undo(self):

        if self.last_action is None:
            return

        action = self.last_action

        if action["type"] == "trash":

            shutil.move(
                action["destination"],
                action["source"],
            )

            self.media.files.insert(
                action["index"],
                action["source"],
            )

            self.media.index = action["index"]

            self.update_view()

            self.toast.show_message("↩ Undo")

        self.last_action = None
    
    def eventFilter(self, obj, event):

        if event.type() == QEvent.MouseMove:
            self.show_overlay()
            self.show_cursor()

        return super().eventFilter(obj, event)
    
    def mousePressEvent(self, event):
        if self.overlay_hidden:
            self.show_overlay()

        super().mousePressEvent(event)