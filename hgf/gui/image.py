# TODO!

from . import base


class Image(base.Entity):
    def __init__(self, filename=None):
        super().__init__(0, 0, hoverable=False, clickable=False)
        self._image = None
        if filename is not None:
            self.load(filename)

    @property
    def image(self):
        return self._image

    @image.setter
    def image(self, other):
        self.image = other
        self.background = self.image
