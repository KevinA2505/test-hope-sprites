import os
import pygame
from spritesheet import SpriteSheet

WIDTH, HEIGHT = 800, 600
GROUND_HEIGHT = HEIGHT // 4

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
        # Use the first frames to determine the physics body size so it stays
        # constant regardless of the current animation frame. Relying on the
        # sprite frame sizes caused jitter when colliding with platforms.
        stand_frame = self.walk_sheet.get_frame(0)
        crouch_frame = self.crouch_sheet.get_frame(0)
        self.width = stand_frame.get_width()
        self.stand_height = stand_frame.get_height()
        self.crouch_height = crouch_frame.get_height()
        self.image = stand_frame
        self.rect = pygame.Rect(0, 0, self.width, self.stand_height)
        self.rect.midbottom = (self.x, self.y)
        self.jump_velocity = -15
        self.jump_prepare = False
        self.jump_prepare_timer = 0
        self.jump_prepare_delay = 150  # milliseconds delay before jumping

    def toggle_crouch(self, obstacles=()):
        if not self.on_ground:
            return
        if self.crouched:
            # attempt to stand - check for space using the standing hit box
            test_rect = pygame.Rect(0, 0, self.width, self.stand_height)
            test_rect.midbottom = (self.x, self.y)
            for ob in obstacles:
                if test_rect.colliderect(ob.rect):
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
            # Jump higher when crouched and stand up immediately
            if self.crouched:
                self.jump_velocity = -15 * 1.15
                self.crouched = False
            else:
                self.jump_velocity = -15

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

    def apply_physics(self, level, dt):
        gravity = 0.8
        if self.jump_prepare:
            self.jump_prepare_timer += dt
            if self.jump_prepare_timer >= self.jump_prepare_delay:
                self.jump_prepare = False
                self.vy = self.jump_velocity
                self.on_ground = False

        if not self.on_ground:
            self.vy += gravity

        # horizontal move
        self.x += self.vx
        self.update_rect()
        self.resolve_collisions(level.platforms, horizontal=True)

        # vertical move
        self.y += self.vy
        self.update_rect()
        self.on_ground = False
        self.resolve_collisions(level.platforms, horizontal=False)

        floor_y = level.height - level.ground_height
        if self.y >= floor_y:
            self.y = floor_y
            self.vy = 0
            self.on_ground = True
            self.update_rect()

        # keep player within level bounds
        self.x = max(self.rect.width // 2, min(level.width - self.rect.width // 2, self.x))
        self.y = max(self.rect.height // 2, min(self.y, floor_y))
        self.update_rect()

    def resolve_collisions(self, platforms, horizontal):
        for p in platforms:
            if self.rect.colliderect(p.rect):
                if horizontal:
                    if self.vx > 0:
                        self.rect.right = p.rect.left
                    elif self.vx < 0:
                        self.rect.left = p.rect.right
                    self.x = self.rect.centerx
                    self.vx = 0
                else:
                    if self.vy > 0:
                        self.rect.bottom = p.rect.top
                        self.y = self.rect.bottom
                        self.on_ground = True
                    elif self.vy < 0:
                        self.rect.top = p.rect.bottom
                        self.y = self.rect.bottom
                    self.vy = 0
                self.update_rect()

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

    def update_rect(self):
        height = self.crouch_height if self.crouched else self.stand_height
        self.rect.width = self.width
        self.rect.height = height
        self.rect.midbottom = (self.x, self.y)

    def draw(self, surface, camera_x=0, camera_y=0):
        self.update_rect()
        surface.blit(self.image, (self.rect.x - camera_x, self.rect.y - camera_y))
