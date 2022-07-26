from PIL import Image


class TransposedFont:

    def __init__(self, font, orientation=None):
        self.font = font
        self.orientation = orientation  # any 'transpose' argument, or None

    def getsize(self, text, *args, **kwargs):
        w, h = self.font.getsize(text)
        if self.orientation in (Image.ROTATE_90, Image.ROTATE_270):
            return h, w
        return w, h

    def getbbox(self, text, *args, **kwargs):
        width, height = self.font.getsize(text)
        if self.orientation in (Image.ROTATE_90, Image.ROTATE_270):
            return 0, 0, height, width
        return 0, 0, width, height

    def getmask(self, text, mode="", *args, **kwargs):
        im = self.font.getmask(text, mode, *args, **kwargs)
        if self.orientation is not None:
            return im.transpose(self.orientation)
        return im
