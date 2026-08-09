from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".gif",
    ".webp",

    # RAW
    ".cr2",
    ".cr3",
    ".nef",
    ".arw",
    ".dng",
    ".rw2",

    # Video
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
}


class MediaFolder:
    def __init__(self, path):
        path = Path(path)

        if path.is_dir():
            self.folder = path
            start_file = None
        else:
            self.folder = path.parent
            start_file = path

        self.files = sorted(
            [
                file
                for file in self.folder.iterdir()
                if file.is_file()
                and file.suffix.lower() in SUPPORTED_EXTENSIONS
            ]
        )

        if start_file is None:
            self.index = 0
        else:
            self.index = self.files.index(start_file)

    def current(self):
        if not self.files:
            return None
        return self.files[self.index]

    def next(self):
        if self.index < len(self.files) - 1:
            self.index += 1
        return self.current()

    def previous(self):
        if self.index > 0:
            self.index -= 1
        return self.current()

    def jump(self, index):
        if 0 <= index < len(self.files):
            self.index = index
        return self.current()

    def count(self):
        return len(self.files)