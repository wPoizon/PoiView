from pathlib import Path

SUPPORTED_EXTENSIONS = {
    ".jpg",
    ".jpeg",
    ".png",
    ".bmp",
    ".gif",
    ".webp",
    ".cr2",
    ".dng",
    ".mp4",
    ".mov",
    ".avi",
    ".mkv",
}


class MediaFolder:
    def __init__(self, folder):
        self.folder = Path(folder)

        self.files = sorted(
            [
                file
                for file in self.folder.iterdir()
                if file.is_file()
                and file.suffix.lower() in SUPPORTED_EXTENSIONS
            ]
        )

        self.index = 0

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