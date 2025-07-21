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
        self.crouch_timer = 0
        self.jump_index = 0
        self.jump_timer = 0
        self.frame_timer = 0
        self.image = self.walk_sheet.get_frame(0)
        self.rect = self.image.get_rect()
        self.jump_prepare = False
        self.jump_prepare_timer = 0
        self.jump_prepare_delay = 150  # milliseconds delay before jumping

    def toggle_crouch(self, obstacles=()):
        if not self.on_ground:
            return
        if self.crouched:
            # attempt to stand - check for space
            test_image = self.walk_sheet.get_frame(0)
            test_rect = test_image.get_rect()
            test_rect.midbottom = (self.x, self.y)
            for ob in obstacles:
                if test_rect.colliderect(ob):
                    return
            self.crouched = False
        else:
            self.crouched = True
        self.crouch_timer = 0
        self.crouch_index = 0

    def start_jump(self):
        if self.on_ground and not self.jump_prepare:
            self.jump_prepare = True
            self.jump_prepare_timer = 0
            self.jump_index = 0
            self.jump_timer = 0

    def handle_input(self, keys, dt):
        speed = 5
        crouch_speed = 3
        self.vx = 0

        left = keys[pygame.K_a] or keys[pygame.K_LEFT]
        right = keys[pygame.K_d] or keys[pygame.K_RIGHT]

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

    def apply_physics(self, obstacles, dt):
        gravity = 0.8
        if self.jump_prepare:
            self.jump_prepare_timer += dt
            if self.jump_prepare_timer >= self.jump_prepare_delay:
                self.jump_prepare = False
                self.vy = -15
                self.on_ground = False

        if not self.on_ground:
            self.vy += gravity

        self.x += self.vx
        self.y += self.vy

        self.rect = self.image.get_rect()
        self.rect.midbottom = (self.x, self.y)

        for ob in obstacles:
            if self.rect.colliderect(ob):
                if self.vy > 0 and self.rect.bottom - self.vy <= ob.top:
                    self.rect.bottom = ob.top
                    self.y = self.rect.bottom
                    self.vy = 0
                    self.on_ground = True
                elif self.vy < 0 and self.rect.top - self.vy >= ob.bottom:
                    self.rect.top = ob.bottom
                    self.y = self.rect.bottom
                    self.vy = 0

        floor_y = HEIGHT - GROUND_HEIGHT
        if self.y >= floor_y:
            self.y = floor_y
            self.vy = 0
            self.on_ground = True
            self.rect.midbottom = (self.x, self.y)

        # keep player inside screen bounds
        self.x = max(self.rect.width // 2, min(WIDTH - self.rect.width // 2, self.x))
        self.rect.midbottom = (self.x, self.y)

    def update_animation(self, dt):
        self.frame_timer += dt
        delay = 100

        if self.on_ground and not self.jump_prepare:
            self.jump_index = 0
            self.jump_timer = 0
            self.crouch_timer += dt
            if self.crouched:
                if self.vx != 0:
                    sheet = self.crouch_move_sheet
                    index = int(self.frame_timer // delay) % sheet.frames
                    self.image = sheet.get_frame(index)
                else:
                    sheet = self.crouch_sheet
                    if self.crouch_index < sheet.frames - 1 and self.crouch_timer >= delay:
                        self.crouch_timer = 0
                        self.crouch_index += 1
                    index = min(self.crouch_index, sheet.frames - 1)
                    self.image = sheet.get_frame(index)
            else:
                self.crouch_index = 0
                if self.vx != 0:
                    sheet = self.walk_sheet
                    index = int(self.frame_timer // delay) % sheet.frames
                    self.image = sheet.get_frame(index)
                else:
                    self.image = self.walk_sheet.get_frame(0)
        elif self.jump_prepare:
            self.jump_timer += dt
            sheet = self.jump_sheet
            if self.jump_index < 1 and self.jump_timer >= delay:
                self.jump_timer = 0
                self.jump_index += 1
            index = min(self.jump_index, 1)
            self.image = sheet.get_frame(index)
        else:
            self.jump_timer += dt
            sheet = self.jump_sheet
            if self.jump_index < 3 and self.jump_timer >= delay:
                self.jump_timer = 0
                self.jump_index += 1
            index = min(self.jump_index, 3)
            self.image = sheet.get_frame(index)
        if self.facing == -1:
            self.image = pygame.transform.flip(self.image, True, False)

    def draw(self, surface):
        self.rect = self.image.get_rect()
        self.rect.midbottom = (self.x, self.y)
        surface.blit(self.image, self.rect)


def main():
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption('Hope Sprite Test')
    clock = pygame.time.Clock()

    player = Player(WIDTH//2, HEIGHT - GROUND_HEIGHT)
    ground_rect = pygame.Rect(0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT)
    platforms = [
        ground_rect,
        pygame.Rect(150, HEIGHT - GROUND_HEIGHT - 120, 200, 20),
        pygame.Rect(450, HEIGHT - GROUND_HEIGHT - 220, 200, 20),
        pygame.Rect(50, HEIGHT - GROUND_HEIGHT - 180, 220, 20),
    ]

    running = True
    while running:
        dt = clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    player.toggle_crouch(platforms)
                elif event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    player.start_jump()

        keys = pygame.key.get_pressed()
        player.handle_input(keys, dt)
        player.apply_physics(platforms, dt)
        player.update_animation(dt)

        screen.fill((255, 255, 255))  # white background
        for p in platforms:
            pygame.draw.rect(screen, (0,0,0), p)
        player.draw(screen)
        pygame.display.flip()

    pygame.quit()

if __name__ == '__main__':
    main()
