import pygame

from player import Player, WIDTH, HEIGHT, GROUND_HEIGHT
from level import Level

class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
        pygame.display.set_caption('Hope Sprite Test')
        self.clock = pygame.time.Clock()
        world_width = WIDTH * 3
        self.level = Level(world_width, HEIGHT, GROUND_HEIGHT)
        self.player = Player(WIDTH // 2, HEIGHT - GROUND_HEIGHT)
        self.running = True

    def run(self):
        while self.running:
            dt = self.clock.tick(60)
            self.handle_events()
            keys = pygame.key.get_pressed()
            self.player.handle_input(keys, dt)
            self.player.apply_physics(self.level, dt)
            self.player.update_animation(dt)
            self.level.update_camera(self.player.x, WIDTH)
            self.draw()
        pygame.quit()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LSHIFT:
                    self.player.toggle_crouch(self.level.platforms)
                elif event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                    self.player.start_jump()

    def draw(self):
        self.screen.fill((255, 255, 255))
        self.level.draw(self.screen, WIDTH)
        self.player.draw(self.screen, self.level.camera_x)
        pygame.display.flip()

if __name__ == '__main__':
    Game().run()