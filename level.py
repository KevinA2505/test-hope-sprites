import pygame

class Platform:
    def __init__(self, rect):
        self.rect = rect
        self.mask = pygame.Mask(rect.size, fill=True)

    def draw(self, surface, camera_x=0):
        pygame.draw.rect(surface, (0, 0, 0), pygame.Rect(self.rect.x - camera_x, self.rect.y, self.rect.width, self.rect.height))

class Level:
    def __init__(self, width, height, ground_height):
        self.width = width
        self.height = height
        self.ground_height = ground_height
        self.platforms = []
        self.generate()
        self.camera_x = 0

    def generate(self):
        h = self.height
        gh = self.ground_height
        self.platforms.append(Platform(pygame.Rect(0, h - gh, self.width, gh)))
        self.platforms.append(Platform(pygame.Rect(150, h - gh - 120, 200, 20)))
        self.platforms.append(Platform(pygame.Rect(450, h - gh - 220, 200, 20)))
        self.platforms.append(Platform(pygame.Rect(50 + 600, h - gh - 180, 220, 20)))
        self.platforms.append(Platform(pygame.Rect(1100, h - gh - 100, 200, 20)))
        self.platforms.append(Platform(pygame.Rect(1600, h - gh - 150, 240, 20)))

    def update_camera(self, player_x, screen_width):
        self.camera_x = max(0, min(player_x - screen_width // 2, self.width - screen_width))

    def draw(self, surface, screen_width):
        for p in self.platforms:
            p.draw(surface, self.camera_x)
