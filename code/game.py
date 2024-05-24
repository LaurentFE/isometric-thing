import sys
import pygame
import code.config as cfg
import code.support as support
import code.tile_set as tile_set


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Game(metaclass=Singleton):
    def __init__(self):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        pygame.display.set_caption(cfg.GAME_NAME)
        self.clock = pygame.time.Clock()
        tile_set.TERRAIN_TILE_SET = tile_set.TileSet(cfg.TILE_TERRAIN)

        self.level = []
        for i in range(4):
            self.level.append(support.import_csv_layout(f'{cfg.MAPS_FOLDER}proto_map_{i}{cfg.MAPS_EXTENSION}'))
        self.level_width = len(self.level[0][0])
        self.level_height = len(self.level[0])

    def display_level(self):
        tile0_x = (cfg.SCREEN_WIDTH - cfg.SPRITE_SIZE) // 2
        tile0_y = 0
        tile_x_offset = cfg.SPRITE_SIZE // 2
        tile_y_offset = cfg.SPRITE_SIZE // 4
        for level_height in range(len(self.level)):
            for i in range(self.level_width):
                for j in range(self.level_height):
                    tile_x = tile0_x + tile_x_offset * (i - j)
                    tile_y = tile0_y + tile_y_offset * (i + j)
                    sprite_id = self.level[level_height][j][i]
                    if sprite_id != '-1':
                        self.screen.blit(tile_set.TERRAIN_TILE_SET.get_sprite_image(int(sprite_id)), (tile_x, tile_y))

    def run(self):
        while True:
            self.screen.fill(cfg.BACKGROUND_COLOR_NAME)

            # Run game loop here before display update
            self.display_level()

            pygame.display.update()
            self.clock.tick(cfg.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()


