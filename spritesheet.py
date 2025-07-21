import pygame

SCALE = 0.15  # scale factor for sprites

class SpriteSheet:
    """Utility class to handle sprite sheets."""
    def __init__(self, path):
        sheet = pygame.image.load(path).convert_alpha()
        self.sheet = sheet
        self.frame_size = sheet.get_height()
        self.frames = sheet.get_width() // self.frame_size

    def get_frame(self, index):
        rect = pygame.Rect(self.frame_size * index, 0, self.frame_size, self.frame_size)
        image = self.sheet.subsurface(rect)
        if SCALE != 1.0:
            w = int(self.frame_size * SCALE)
            h = int(self.frame_size * SCALE)
            image = pygame.transform.scale(image, (w, h))
        return image
