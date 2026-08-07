from PySide6.QtCore import Qt, QTimer, QEvent, QPoint
from PySide6.QtWidgets import (
    QApplication,
    QLabel,
    QMainWindow,
    QMessageBox,
    QStackedWidget,
    QSizePolicy,
)

from PySide6.QtGui import QPixmap, QPainter

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
    
    def __init__(self, file, cache_amount=10):
        super().__init__()
        
        self.cache_amount = cache_amount
        
        self.media = MediaFolder(file)
        self.cache = ImageCache(max_items=cache_amount * 2 + 1)
        self.video = VideoLoader()
        
        folder = self.media.folder

        self.favourites_folder = folder / "favourites"
        self.favourites_folder.mkdir(exist_ok=True)

        self.trash_folder = folder / "trash"
        self.trash_folder.mkdir(exist_ok=True)

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        
        self.zoom = 1.0
        self.pan_offset = QPoint(0, 0)
        self.zoom_center = QPoint(0, 0)
        self.dragging = False
        self.last_mouse_pos = None
        self.original_pixmap = None
        
        self.label.setSizePolicy(
            QSizePolicy.Ignored,
            QSizePolicy.Ignored,
        )

        self.label.setScaledContents(False)
        
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
        self.label.setFocusPolicy(Qt.StrongFocus)
        self.label.setAttribute(Qt.WA_AcceptTouchEvents, True)
        self.label.installEventFilter(self)

        self.video.widget.setMouseTracking(True)
        self.overlay.setGeometry(self.rect())
        self.overlay.show()
        self.overlay.raise_()

        self.update_view()
        self.video.resize(self.stack.size())
        self.overlay_hidden = False
        
        QApplication.instance().installEventFilter(self)
        
        
    def update_image(self):

        if self.original_pixmap is None:
            return

        base = self.original_pixmap.scaled(
            self.stack.size(),
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        scaled = base.scaled(
            base.size() * self.zoom,
            Qt.KeepAspectRatio,
            Qt.SmoothTransformation,
        )

        canvas = QPixmap(self.stack.size())
        canvas.fill(Qt.transparent)

        painter = QPainter(canvas)

        x = (
            (canvas.width() - scaled.width()) // 2
            + self.pan_offset.x()
        )

        y = (
            (canvas.height() - scaled.height()) // 2
            + self.pan_offset.y()
        )

        painter.drawPixmap(x, y, scaled)
        painter.end()

        self.label.setPixmap(canvas)


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

            self.original_pixmap = self.cache.get(current)

            self.update_image()

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
            print("TOGGLE:", self.geometry(), self.frameGeometry())
        else:
            self.setWindowState(
                self.windowState() | Qt.WindowFullScreen
            )
            print("TOGGLE:", self.geometry(), self.frameGeometry())
        QTimer.singleShot(200, self.update_view)


    def mouseDoubleClickEvent(self, event):
        self.toggle_fullscreen()
        super().mouseDoubleClickEvent(event)
        
    def wheelEvent(self, event):
        current = self.media.current()

        if current is None:
            return

        if self.video.is_video(current):

            if event.angleDelta().y() > 0:
                self.video.zoom_at(
                    event.position().toPoint(),
                    1.1
                )
            else:
                self.video.zoom_at(
                    event.position().toPoint(),
                    1 / 1.1
                )
            event.accept()
            return

        mouse_pos = event.position().toPoint()

        old_zoom = self.zoom

        if event.angleDelta().y() > 0:
            self.zoom *= 1.1
        else:
            self.zoom /= 1.1

        self.zoom = max(1.0, min(self.zoom, 5.0))

        scale_change = self.zoom / old_zoom
        
        if self.zoom == 1.0:
            self.pan_offset = QPoint(0, 0)

        center = QPoint(
            self.stack.width() // 2,
            self.stack.height() // 2,
        )

        mouse_offset = mouse_pos - center

        self.pan_offset = (
            self.pan_offset
            - mouse_offset * (scale_change - 1)
        )

        self.update_image()


    def mouseMoveEvent(self, event):
        if self.dragging and self.zoom > 1.0:
            current = event.position().toPoint()

            delta = current - self.last_mouse_pos
            self.pan_offset += delta

            self.last_mouse_pos = current

            self.update_view()

        super().mouseMoveEvent(event)


    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False

        super().mouseReleaseEvent(event)
        
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
            QTimer.singleShot(200, self.resize)
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
        super().resizeEvent(event)

        self.overlay.setGeometry(self.rect())
        self.video.resize(self.stack.size())
        self.overlay.raise_()
        
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
        
        print(
            "WINDOW:", self.windowHandle().size(),
            "MAIN:", self.size(),
            "STACK:", self.stack.size(),
            "LABEL:", self.label.size()
        )

        self.update_image()


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

        if obj == self.label:

            if event.type() == QEvent.Wheel:
                self.wheelEvent(event)
                return True

            if event.type() == QEvent.MouseButtonPress:
                self.mousePressEvent(event)
                return True

            if event.type() == QEvent.MouseMove:
                self.mouseMoveEvent(event)
                return True

            if event.type() == QEvent.MouseButtonRelease:
                self.mouseReleaseEvent(event)
                return True

        if event.type() == QEvent.MouseMove:
            self.show_overlay()
            self.show_cursor()

        return super().eventFilter(obj, event)
    
    def mousePressEvent(self, event):

        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.last_mouse_pos = event.position().toPoint()

        if self.overlay_hidden:
            self.show_overlay()

        super().mousePressEvent(event)