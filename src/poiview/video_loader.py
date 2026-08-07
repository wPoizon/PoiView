from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtMultimedia import QAudioOutput, QMediaPlayer
from PySide6.QtWidgets import QGraphicsScene, QGraphicsView
from PySide6.QtMultimediaWidgets import QGraphicsVideoItem
from PySide6.QtCore import Qt
from PySide6.QtCore import QRectF, QPointF, QSizeF


VIDEO_EXTENSIONS = {
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
}


class VideoView(QGraphicsView):

    def wheelEvent(self, event):
        event.accept()


class VideoLoader:

    def __init__(self):
        self.scene = QGraphicsScene()

        self.video_item = QGraphicsVideoItem()
        self.scene.addItem(self.video_item)
        
        self.zoom = 1.0

        self.widget = VideoView(self.scene)
        self.widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.widget.setTransformationAnchor(QGraphicsView.NoAnchor)
        self.widget.setResizeAnchor(QGraphicsView.NoAnchor)
        self.widget.setFocusPolicy(Qt.NoFocus)
        self.widget.setFrameShape(QGraphicsView.NoFrame)

        self.player = QMediaPlayer()
        self.audio = QAudioOutput()

        self.player.setAudioOutput(self.audio)
        self.player.setVideoOutput(self.video_item)
        
        self.positionChanged = self.player.positionChanged
        self.durationChanged = self.player.durationChanged
        self.mediaStatusChanged = self.player.mediaStatusChanged
        self.playbackStateChanged = self.player.playbackStateChanged
        

    def load(self, path):

        path = Path(path)

        self.player.stop()

        self.player.setSource(
            QUrl.fromLocalFile(str(path))
        )

        self.player.play()

    def stop(self):
        self.player.stop()

    def play(self):
        self.player.play()

    def pause(self):
        self.player.pause()

    def toggle_pause(self):
        if self.is_playing():
            self.pause()
        else:
            self.play()

    def seek(self, position):
        self.player.setPosition(position)

    def position(self):
        return self.player.position()

    def duration(self):
        return self.player.duration()

    def is_playing(self):
        return (
            self.player.playbackState()
            == QMediaPlayer.PlayingState
        )

    def is_video(self, path):
        return Path(path).suffix.lower() in VIDEO_EXTENSIONS
    
    def resize(self, size):
        self.video_item.setSize(size)

        self.scene.setSceneRect(
            QRectF(
                QPointF(0, 0),
                QSizeF(size),
            )
        )
        
    def zoom_at(self, pos, factor):

        old_pos = self.widget.mapToScene(pos)

        self.zoom *= factor
        self.zoom = max(1.0, min(self.zoom, 5.0))

        self.widget.resetTransform()
        self.widget.scale(self.zoom, self.zoom)

        new_pos = self.widget.mapToScene(pos)

        delta = new_pos - old_pos
        self.widget.translate(delta.x(), delta.y())
