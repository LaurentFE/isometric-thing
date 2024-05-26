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


# Takes in char_coord as seen in default view (North), returns x,y,z in context of the specified camera orientation
def get_orientation_coord(map_width: int, map_length: int, char_coord: tuple, camera_orientation: str):
    if camera_orientation == cfg.CAMERA_WEST:
        x = map_width - 1 - char_coord[1]
        y = char_coord[0]
    elif camera_orientation == cfg.CAMERA_EAST:
        x = char_coord[1]
        y = map_length - 1 - char_coord[0]
    elif camera_orientation == cfg.CAMERA_SOUTH:
        x = map_width - 1 - char_coord[0]
        y = map_length - 1 - char_coord[1]
    else:
        if camera_orientation != cfg.CAMERA_NORTH:
            print(cfg.UNKNOWN_CAMERA_ORIENTATION, ':', camera_orientation, file=sys.stderr, flush=True)
        x = char_coord[0]
        y = char_coord[1]

    return x, y, char_coord[2]


# Takes in tile_coord in context of the camera_orientation, returns the correct sprite_id from the unmodified
# (north oriented) default sprite_map
def get_orientation_tile_sprite(sprite_map: list, tile_coord: tuple, camera_orientation: str):
    length = len(sprite_map[0])
    width = len(sprite_map[0][0])
    if camera_orientation == cfg.CAMERA_WEST:
        sprite_id = sprite_map[tile_coord[2]][length - 1 - tile_coord[0]][tile_coord[1]]
    elif camera_orientation == cfg.CAMERA_EAST:
        sprite_id = sprite_map[tile_coord[2]][tile_coord[0]][width - 1 - tile_coord[1]]
    elif camera_orientation == cfg.CAMERA_SOUTH:
        sprite_id = sprite_map[tile_coord[2]][length - 1 - tile_coord[1]][width - 1 - tile_coord[0]]
    else:
        if camera_orientation != cfg.CAMERA_NORTH:
            print(cfg.UNKNOWN_CAMERA_ORIENTATION, ':', camera_orientation, file=sys.stderr, flush=True)
        sprite_id = sprite_map[tile_coord[2]][tile_coord[1]][tile_coord[0]]

    return sprite_id


# Coordinates received are the tile x,y,z in context of the current camera rotation
def get_sprite_rect(sprite_coord: tuple, is_character=False):
    if len(sprite_coord) != 3:
        raise ValueError(cfg.INCORRECT_COORD_FORMAT + ' : ' + sprite_coord)

    height_adjusted_x = sprite_coord[0] - sprite_coord[2]
    height_adjusted_y = sprite_coord[1] - sprite_coord[2]
    display_x = cfg.TILE0_X + cfg.TILE_X_OFFSET * (height_adjusted_x - height_adjusted_y)
    display_y = cfg.TILE0_Y + cfg.TILE_Y_OFFSET * (height_adjusted_x + height_adjusted_y)

    if is_character:
        display_x += cfg.CHARACTER_X_CENTER_OFFSET
        display_y += cfg.CHARACTER_Y_CENTER_OFFSET

    return pygame.Rect(display_x, display_y, cfg.SPRITE_SIZE, cfg.SPRITE_SIZE)


# Coordinates received are the tile x,y,z in context of the current camera rotation
# Player coordinates are adjusted to the x,y,z in context of the current camera rotation
def is_character_behind_tile(tile_coord: tuple, char_coord: tuple):
    if len(tile_coord) != 3:
        raise ValueError(cfg.INCORRECT_COORD_FORMAT + ' : ' + tile_coord)
    elif len(char_coord) != 3:
        raise ValueError(cfg.INCORRECT_COORD_FORMAT + ' : ' + char_coord)

    t_x = tile_coord[0]
    t_y = tile_coord[1]
    t_z = tile_coord[2]
    c_x = char_coord[0]
    c_y = char_coord[1]
    c_z = char_coord[2]
    player_height_diff = t_z - c_z
    tile_rect = get_sprite_rect(tile_coord)
    player_rect = get_sprite_rect(char_coord, True)

    if (player_height_diff > 0
            and t_x >= c_x
            and t_y >= c_y
            and tile_rect.colliderect(player_rect)):
        return True
    else:
        return False


class Game(metaclass=Singleton):
    def __init__(self):
        # general setup
        pygame.init()
        self.screen = pygame.display.set_mode((cfg.SCREEN_WIDTH, cfg.SCREEN_HEIGHT))
        pygame.display.set_caption(cfg.GAME_NAME)
        self.clock = pygame.time.Clock()
        tile_set.TERRAIN_TILE_SET = tile_set.TileSet(cfg.TILE_TERRAIN)

        # BIG PREREQUISITE FOR CAMERA SO FAR : SQUARE MAP NOT RECTANGULAR !!
        # If I want to use rectangular maps, I will need to create different lists that can be read for each view
        # At least two, for the couples of views that don't share width & length.
        self.map = []
        self.map_name = 'proto_map_homemade'
        for i in range(3):
            self.map.append(support.import_csv_layout(f'{cfg.MAPS_FOLDER}{self.map_name}_{i}{cfg.MAPS_EXTENSION}'))
        self.map_width = len(self.map[0][0])
        self.map_length = len(self.map[0])

        self.char_test_tileset = tile_set.TileSet(cfg.TILE_CHARACTER, cfg.CHARACTER_TEST)
        self.player_x = 2
        self.player_y = 2
        self.player_z = 0

    def get_player_coord(self):
        return self.player_x, self.player_y, self.player_z

    def display_level(self, camera_orientation: str):
        for map_x in range(self.map_width):
            for map_y in range(self.map_length):
                for map_z in range(len(self.map)):
                    if camera_orientation not in cfg.CAMERA_ORIENTATIONS:
                        print(cfg.UNKNOWN_CAMERA_ORIENTATION, ':', camera_orientation, file=sys.stderr, flush=True)
                        camera_orientation = cfg.CAMERA_NORTH

                    sprite_id = get_orientation_tile_sprite(self.map, (map_x, map_y, map_z), camera_orientation)
                    player_x, player_y, player_z = get_orientation_coord(self.map_width,
                                                                         self.map_length,
                                                                         self.get_player_coord(),
                                                                         camera_orientation)
                    if sprite_id != '-1':
                        sprite = tile_set.TERRAIN_TILE_SET.get_sprite_image(int(sprite_id), camera_orientation)
                        # Make a tile translucent to reveal character behind
                        if is_character_behind_tile((map_x, map_y, map_z),
                                                    (player_x, player_y, player_z)):
                            sprite.set_alpha(128)
                        self.screen.blit(sprite, get_sprite_rect((map_x, map_y, map_z)))

                    # Draws a character at its proper coordinates
                    # Redraws a character if a tile behind it but higher hides the previous character drawing
                    if player_x == map_x and player_y == map_y and player_z == map_z:
                        self.screen.blit(self.char_test_tileset.get_sprite_image(0, camera_orientation),
                                         get_sprite_rect((map_x, map_y, map_z+1), True))

                    if sprite_id != '-1':
                        pygame.display.update()
                        time.sleep(0.05)

    def run_old(self):
        camera_orientation = 0
        while True:
            self.screen.fill(cfg.BACKGROUND_COLOR_NAME)

            # Run game loop here before display update
            self.display_level(cfg.CAMERA_ORIENTATIONS[camera_orientation])

            pygame.display.update()
            self.clock.tick(cfg.FPS)

            camera_orientation = (camera_orientation + 1) % len(cfg.CAMERA_ORIENTATIONS)
            time.sleep(2)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

    def run(self):
        for camera_orientation in range(len(cfg.CAMERA_ORIENTATIONS)):
            self.screen.fill(cfg.BACKGROUND_COLOR_NAME)

            # Displays drawing tile by tile
            # Requires adding pygame.display.update() and a timer.sleep(0.1) at the end of display_level()
            # Better to put it in an if sprite_id != -1
            self.display_level(cfg.CAMERA_ORIENTATIONS[camera_orientation])

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
