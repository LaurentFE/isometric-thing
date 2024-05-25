import sys
import pygame
import src.config as cfg
import src.support as support
import src.tile_set as tile_set
import time


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

        # BIG PREREQUISITE FOR CAMERA SO FAR : SQUARE MAP NOT RECTANGULAR !!
        self.level = []
        self.map_name = 'proto_map_homemade'
        for i in range(3):
            self.level.append(support.import_csv_layout(f'{cfg.MAPS_FOLDER}{self.map_name}_{i}{cfg.MAPS_EXTENSION}'))
        self.level_width = len(self.level[0][0])
        self.level_length = len(self.level[0])

        self.char_test_tileset = tile_set.TileSet(cfg.TILE_CHARACTER, cfg.CHARACTER_TEST)
        self.player_pos_x = 2
        self.player_pos_y = 2
        self.player_height = 0
        self.player_sprite_homemade_x = (cfg.SCREEN_WIDTH - cfg.SPRITE_SIZE) // 2 + cfg.SPRITE_SIZE // 2 * (self.player_pos_x - self.player_pos_y) + cfg.CHARACTER_X_CENTER_OFFSET
        self.player_sprite_homemade_y = cfg.SPRITE_SIZE + cfg.SPRITE_SIZE // 4 * (self.player_pos_x + self.player_pos_y) + cfg.CHARACTER_Y_CENTER_OFFSET - cfg.SPRITE_SIZE // 2
        self.player_homemade_rect = pygame.Rect(self.player_sprite_homemade_x, self.player_sprite_homemade_y, cfg.SPRITE_SIZE, cfg.SPRITE_SIZE)
        self.player_sprite_tiled_x = (cfg.SCREEN_WIDTH - cfg.SPRITE_SIZE) // 2 + cfg.SPRITE_SIZE // 2 * (self.player_pos_x - self.player_pos_y)
        self.player_sprite_tiled_y = cfg.SPRITE_SIZE + cfg.SPRITE_SIZE // 4 * (self.player_pos_x + self.player_pos_y) + cfg.CHARACTER_Y_CENTER_OFFSET - cfg.SPRITE_SIZE // 2
        self.player_tiled_rect = pygame.Rect(self.player_sprite_tiled_x, self.player_sprite_tiled_y, cfg.SPRITE_SIZE, cfg.SPRITE_SIZE)

    def display_level_tiled(self):
        tile0_x = (cfg.SCREEN_WIDTH - cfg.SPRITE_SIZE) // 2
        tile0_y = cfg.SPRITE_SIZE
        tile_x_offset = cfg.SPRITE_SIZE // 2
        tile_y_offset = cfg.SPRITE_SIZE // 4

        for level_height in range(len(self.level)):
            for i in range(self.level_width):
                for j in range(self.level_length):
                    tile_x = tile0_x + tile_x_offset * (i - j)
                    tile_y = tile0_y + tile_y_offset * (i + j)

                    sprite_id = self.level[level_height][j][i]
                    if sprite_id != '-1':
                        sprite = tile_set.TERRAIN_TILE_SET.get_sprite_image(int(sprite_id))
                        sprite_rect = pygame.Rect(tile_x, tile_y, cfg.SPRITE_SIZE, cfg.SPRITE_SIZE)
                        player_height_diff = level_height - self.player_height
                        # if (player_height_diff > 0
                        #        and ((i == (self.player_pos_x + 1 - player_height_diff) and j == (self.player_pos_y - player_height_diff))
                        #             or (i == (self.player_pos_x - player_height_diff) and j == (self.player_pos_y + 1 - player_height_diff)))):
                        # if (self.player_pos_x == (i + 1) or self.player_pos_y == (j + 1)) and self.player_height == (level_height - 1):
                        if (player_height_diff > 0
                                and sprite_rect.colliderect(self.player_tiled_rect)):
                            sprite.set_alpha(128)
                        self.screen.blit(sprite, (tile_x, tile_y))

                    if self.player_pos_x == i and self.player_pos_y == j and self.player_height == level_height:
                        self.screen.blit(
                            self.char_test_tileset.get_sprite_image(0, cfg.CAMERA_NORTH),
                            (tile_x + cfg.CHARACTER_X_CENTER_OFFSET,
                             tile_y + cfg.CHARACTER_Y_CENTER_OFFSET - cfg.SPRITE_SIZE//2)
                        )

    def display_level_homemade(self, camera_orientation):
        tile0_x = (cfg.SCREEN_WIDTH - cfg.SPRITE_SIZE) // 2
        tile0_y = cfg.SPRITE_SIZE
        tile_x_offset = cfg.SPRITE_SIZE // 2
        tile_y_offset = cfg.SPRITE_SIZE // 4
        player_x = self.player_pos_x
        player_y = self.player_pos_y
        for level_height in range(len(self.level)):
            for i in range(self.level_width):
                for j in range(self.level_length):
                    x = i - level_height
                    y = j - level_height
                    tile_x = tile0_x + tile_x_offset * (x - y)
                    tile_y = tile0_y + tile_y_offset * (x + y)

                    if camera_orientation == cfg.CAMERA_WEST:
                        sprite_id = self.level[level_height][self.level_length - 1 - i][j]
                        player_x = self.level_width - 1 - self.player_pos_y
                        player_y = self.player_pos_x
                    elif camera_orientation == cfg.CAMERA_EAST:
                        sprite_id = self.level[level_height][i][self.level_width - 1 - j]
                        player_x = self.player_pos_y
                        player_y = self.level_length - 1 - self.player_pos_x
                    elif camera_orientation == cfg.CAMERA_SOUTH:
                        sprite_id = self.level[level_height][self.level_length - 1 - j][self.level_width - 1 - i]
                        player_x = self.level_width - 1 - self.player_pos_x
                        player_y = self.level_length - 1 - self.player_pos_y
                    else:
                        if camera_orientation != cfg.CAMERA_NORTH:
                            print(cfg.UNKNOWN_CAMERA_ORIENTATION, ':', camera_orientation, file=sys.stderr, flush=True)
                            camera_orientation = cfg.CAMERA_NORTH
                        sprite_id = self.level[level_height][j][i]
                    if sprite_id != '-1':
                        sprite = tile_set.TERRAIN_TILE_SET.get_sprite_image(int(sprite_id), camera_orientation)
                        sprite_rect = pygame.Rect(tile_x, tile_y, cfg.SPRITE_SIZE, cfg.SPRITE_SIZE)
                        player_height_diff = level_height - self.player_height
                        if (player_height_diff > 0
                                and i >= self.player_pos_x
                                and j >= self.player_pos_y
                                and sprite_rect.colliderect(self.player_tiled_rect)):
                            sprite.set_alpha(128)
                        self.screen.blit(sprite, (tile_x, tile_y))

                    # Need to change when player is drawn, works for NORTH, but not for other orientations
                    # Currently doesn't account for player_height in its position
                    if player_x == i and player_y == j and self.player_height == level_height:
                        self.screen.blit(
                            self.char_test_tileset.get_sprite_image(0, camera_orientation),
                            (tile_x + cfg.CHARACTER_X_CENTER_OFFSET,
                             tile_y + cfg.CHARACTER_Y_CENTER_OFFSET - cfg.SPRITE_SIZE//2)
                        )
                    if sprite_id != '-1':
                        pygame.display.update()
                        time.sleep(0.2)

    def run_old(self):
        camera_orientation = 0
        while True:
            self.screen.fill(cfg.BACKGROUND_COLOR_NAME)

            # Run game loop here before display update
            self.display_level_homemade(cfg.CAMERA_ORIENTATIONS[camera_orientation])

            pygame.display.update()
            self.clock.tick(cfg.FPS)

            camera_orientation = (camera_orientation + 1) % len(cfg.CAMERA_ORIENTATIONS)
            time.sleep(2)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def run(self):
        camera_orientation = 1

        self.screen.fill(cfg.BACKGROUND_COLOR_NAME)

        # Displays drawing tile by tile, remember to remove the sleep and display.update from display_level_homemade()
        # when you want to go back to run_old()
        self.display_level_homemade(cfg.CAMERA_ORIENTATIONS[camera_orientation])

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
