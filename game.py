import pygame
import os

WIDTH, HEIGHT = 800, 600
GROUND_HEIGHT = HEIGHT // 4

SCALE = 0.15  # scale factor for sprites

class SpriteSheet:
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

class Player:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.vx = 0
        self.vy = 0
        self.on_ground = True
        self.crouched = False
        self.facing = 1
        self.walk_sheet = SpriteSheet(os.path.join('assets','img','sprite hope walking.png'))
        self.crouch_sheet = SpriteSheet(os.path.join('assets','img','sprite hope crouching.png'))
        self.crouch_move_sheet = SpriteSheet(os.path.join('assets','img','sprite hope crouching movement.png'))
        self.jump_sheet = SpriteSheet(os.path.join('assets','img','sprite hope jumping.png'))
        self.walk_index = 0
        self.crouch_index = 0
        self.crouch_move_index = 0
        self.frame_timer = 0
        self.image = self.walk_sheet.get_frame(0)
        self.rect = self.image.get_rect()

    def handle_input(self, keys, dt):
        speed = 5
        crouch_speed = 3
        self.vx = 0
        self.crouched = keys[pygame.K_LSHIFT]

        left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]
        jump = keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]

        if self.crouched:
            if left:
                self.vx = -crouch_speed
                self.facing = -1
            elif right:
                self.vx = crouch_speed
                self.facing = 1
        else:
            if left:
                self.vx = -speed
                self.facing = -1
            elif right:
                self.vx = speed
                self.facing = 1

        if jump and self.on_ground:
            self.vy = -15
            self.on_ground = False

    def apply_physics(self):
        gravity = 0.8
        if not self.on_ground:
            self.vy += gravity
        self.x += self.vx
        self.y += self.vy

        floor_y = HEIGHT - GROUND_HEIGHT
        if self.y >= floor_y:
            self.y = floor_y
            self.vy = 0
            self.on_ground = True

    def update_animation(self, dt):
        self.frame_timer += dt
        delay = 100
        if self.on_ground:
            if self.crouched:
                if self.vx != 0:
                    sheet = self.crouch_move_sheet
                    index = int(self.frame_timer // delay) % sheet.frames
                    self.image = sheet.get_frame(index)
                else:
                    sheet = self.crouch_sheet
                    index = int(self.frame_timer // delay) % sheet.frames
                    self.image = sheet.get_frame(index)
            else:
                if self.vx != 0:
                    sheet = self.walk_sheet
                    index = int(self.frame_timer // delay) % sheet.frames
                    self.image = sheet.get_frame(index)
                else:
                    self.image = self.walk_sheet.get_frame(0)
        else:
            # jumping: use frame 4 (index 3) while in air
            self.image = self.jump_sheet.get_frame(3)
        if self.facing == -1:
            self.image = pygame.transform.flip(self.image, True, False)

    def draw(self, surface):
        rect = self.image.get_rect()
        rect.midbottom = (self.x, self.y)
        surface.blit(self.image, rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption('Hope Sprite Test')
    clock = pygame.time.Clock()

    player = Player(WIDTH//2, HEIGHT - GROUND_HEIGHT)

    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        keys = pygame.key.get_pressed()
        player.handle_input(keys, dt)
        player.apply_physics()
        player.update_animation(dt)

        screen.fill((255, 255, 255))  # white background
        pygame.draw.rect(screen, (0,0,0), (0, HEIGHT-GROUND_HEIGHT, WIDTH, GROUND_HEIGHT))
        player.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
