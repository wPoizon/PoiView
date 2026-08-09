 
from collections import OrderedDict
from threading import Lock
from PySide6.QtCore import QObject, QRunnable, QThreadPool, Signal
from PySide6.QtGui import QPixmap

from poiview.image_loader import ImageLoader

from pathlib import Path

from poiview.video_loader import VIDEO_EXTENSIONS

class PreloadTask(QRunnable):

    def __init__(self, cache, path):
        super().__init__()

        self.cache = cache
        self.path = str(path)

    def run(self):

        try:
            image = self.cache._load(self.path)
        except Exception:
            image = None

        with self.cache.lock:

            self.cache.pending.discard(self.path)

            if image is None:
                return

            if self.path in self.cache.cache:
                return

            self.cache.cache[self.path] = image

            while len(self.cache.cache) > self.cache.max_items:
                self.cache.cache.popitem(last=False)
        self.cache.imageLoaded.emit(self.path)

class ImageCache(QObject):

    imageLoaded = Signal(str)

    def __init__(self, max_items=11):
        super().__init__()

        self.max_items = max_items
        self.cache = OrderedDict()
        self.lock = Lock()
        self.thread_pool = QThreadPool()
        self.thread_pool.setMaxThreadCount(2)
        self.pending = set()
        
    def cached(self, paths):
        with self.lock:
            return sum(
                str(path) in self.cache
                for path in paths
            )

    def get(self, path):
        path = str(path)

        with self.lock:
            if path in self.cache:
                self.cache.move_to_end(path)
                return QPixmap.fromImage(self.cache[path])

        # Ladda UTANFÖR låset
        try:
            image = self._load(path)
        except Exception:
            return None

        with self.lock:

            # Någon annan tråd kan ha hunnit lägga in bilden
            if path in self.cache:
                self.cache.move_to_end(path)
                return QPixmap.fromImage(self.cache[path])

            self.cache[path] = image

            while len(self.cache) > self.max_items:
                self.cache.popitem(last=False)

            return QPixmap.fromImage(image)
        
    def contains(self, path):
        path = str(path)

        with self.lock:
            return path in self.cache

    def preload(self, paths):

        for path in paths:

            path = str(path)

            with self.lock:
                if (
                    path in self.cache
                    or path in self.pending
                ):
                    continue

                self.pending.add(path)

            self.thread_pool.start(
                PreloadTask(self, path),
                0,
            )
            
    def preload_priority(self, path):

        path = str(path)

        with self.lock:
            if (
                path in self.cache
                or path in self.pending
            ):
                return

            self.pending.add(path)

        self.thread_pool.start(
            PreloadTask(self, path),
            1,
        )

    def _load(self, path):

        if Path(path).suffix.lower() in VIDEO_EXTENSIONS:
            return None

        return ImageLoader.load(path)

    def clear(self):
        self.cache.clear()


    def shutdown(self):
        self.thread_pool.clear()