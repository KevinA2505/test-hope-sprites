import pygame

PLATFORM_COLLISION_HEIGHT = 10

class Platform:
    def __init__(self, rect, collision_height=None):
        """Create a platform.

        Parameters
        ----------
        rect : pygame.Rect
            Visual rectangle of the platform.
        collision_height : int, optional
            Height of the collision area. If ``None`` the full ``rect`` height
            is used.
        """
        self.draw_rect = rect
        if collision_height is None:
            collision_height = rect.height
        self.rect = pygame.Rect(rect.x, rect.y, rect.width, collision_height)
        self.mask = pygame.Mask(self.rect.size, fill=True)

    def draw(self, surface, camera_x=0, camera_y=0):
        pygame.draw.rect(
            surface,
            (0, 0, 0),
            pygame.Rect(
                self.draw_rect.x - camera_x,
                self.draw_rect.y - camera_y,
                self.draw_rect.width,
                self.draw_rect.height,
            ),
        )

class Level:
    def __init__(self, width, height, ground_height, player_start=None):
        self.width = width
        self.height = height
        self.ground_height = ground_height
        self.platforms = []
        self.generate(player_start)
        self.camera_x = 0
        self.camera_y = 0

    def generate(self, player_start=None):
        import random

        h = self.height
        gh = self.ground_height

        # Base ground uses full height for collisions
        self.platforms.append(
            Platform(pygame.Rect(0, h - gh, self.width, gh), collision_height=gh)
        )

        margin = 60
        last_y = h - gh - 120
        for _ in range(10):
            y = last_y
            x = random.randint(50, max(50, self.width - 250))
            rect = pygame.Rect(x, y, 200, 20)

            if player_start:
                px, py = player_start
                area = pygame.Rect(px - margin, py - margin, margin * 2, margin * 2)
                if rect.colliderect(area):
                    if x < px:
                        x = max(0, px - rect.width - margin)
                    else:
                        x = min(self.width - rect.width, px + margin)
                    rect.x = x

            self.platforms.append(
                Platform(rect, collision_height=PLATFORM_COLLISION_HEIGHT)
            )
            # place next platform higher up with some variation
            last_y -= random.randint(120, 200)

    def update_camera(self, player_x, player_y, screen_width, screen_height):
        self.camera_x = max(0, min(player_x - screen_width // 2, self.width - screen_width))
        self.camera_y = max(0, min(player_y - screen_height // 2, self.height - screen_height))

    def draw(self, surface, screen_width, screen_height):
        for p in self.platforms:
            p.draw(surface, self.camera_x, self.camera_y)
