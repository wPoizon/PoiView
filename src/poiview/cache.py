 
from collections import OrderedDict
from threading import Lock
from PySide6.QtCore import QRunnable, QThreadPool

from poiview.image_loader import ImageLoader

from pathlib import Path

from poiview.video_loader import VIDEO_EXTENSIONS

class PreloadTask(QRunnable):

    def __init__(self, cache, path):
        super().__init__()

        self.cache = cache
        self.path = str(path)

    def run(self):

        with self.cache.lock:

            if self.path in self.cache.cache:
                return

        pixmap = self.cache._load(self.path)

        with self.cache.lock:

            if self.path in self.cache.cache:
                return

            self.cache.cache[self.path] = pixmap

            while len(self.cache.cache) > self.cache.max_items:
                self.cache.cache.popitem(last=False)

class ImageCache:

    def __init__(self, max_items=11):
        self.max_items = max_items
        self.cache = OrderedDict()
        self.lock = Lock()
        self.thread_pool = QThreadPool.globalInstance()

    def get(self, path):
        path = str(path)

        with self.lock:
            if path in self.cache:
                self.cache.move_to_end(path)
                return self.cache[path]

        # Ladda UTANFÖR låset
        pixmap = self._load(path)

        with self.lock:

            # Någon annan tråd kan ha hunnit lägga in bilden
            if path in self.cache:
                self.cache.move_to_end(path)
                return self.cache[path]

            self.cache[path] = pixmap

            while len(self.cache) > self.max_items:
                self.cache.popitem(last=False)

            return pixmap

    def preload(self, paths):

        for path in paths:

            path = str(path)

            with self.lock:
                if path in self.cache:
                    continue

            self.thread_pool.start(
                PreloadTask(self, path)
            )
                
    def _load(self, path):

        if Path(path).suffix.lower() in VIDEO_EXTENSIONS:
            return None

        return ImageLoader.load(path)

    def clear(self):
        self.cache.clear()