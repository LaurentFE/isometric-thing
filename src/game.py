import sys
import pygame
import src.config as cfg
import src.support as sup
import src.tile_set as tile_set
import src.character as character


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class Game(metaclass=Singleton):
    def __init__(self) -> None:
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
        for i in range(4):
            self.map.append(sup.import_csv_layout(f'{cfg.MAPS_FOLDER}{self.map_name}_{i}{cfg.MAPS_EXTENSION}'))
        self.camera_orientation = cfg.CAMERA_NORTH

        self.test_character = character.Character((), cfg.CHARACTER_TEST, (2, 2, 2))
        self.key_pressed_start_timer = 0
        self.key_pressed_cooldown = cfg.KEY_PRESSED_COOLDOWN

    def display_level(self, camera_orientation: str) -> None:
        for map_x in range(cfg.MAP_WIDTH):
            for map_y in range(cfg.MAP_LENGTH):
                for map_z in range(len(self.map)):
                    if camera_orientation not in cfg.CAMERA_ORIENTATIONS:
                        print(cfg.UNKNOWN_CAMERA_ORIENTATION, ':', camera_orientation, file=sys.stderr, flush=True)
                        camera_orientation = cfg.CAMERA_NORTH

                    sprite_id = sup.get_orientation_tile_sprite_id(self.map,
                                                                   (map_x, map_y, map_z),
                                                                   camera_orientation)
                    player_x, player_y, player_z = self.test_character.get_orientation_coord(camera_orientation)
                    if sprite_id != '-1':
                        sprite = tile_set.TERRAIN_TILE_SET.get_sprite_image(int(sprite_id), camera_orientation)
                        # Make a tile translucent to reveal character behind
                        if self.test_character.is_character_behind_tile((map_x, map_y, map_z),
                                                                        camera_orientation):
                            sprite.set_alpha(128)
                        self.screen.blit(sprite, sup.get_sprite_rect((map_x, map_y, map_z)))

                    # Draws a character at its proper coordinates
                    # Redraws a character if a tile behind it but higher hides the previous character drawing
                    if player_x == map_x and player_y == map_y and player_z == map_z:
                        self.screen.blit(self.test_character.get_display_sprite(camera_orientation),
                                         self.test_character.get_rectangle(camera_orientation))

    def handle_input(self, inputs: list) -> None:
        current_time = pygame.time.get_ticks()
        if current_time - self.key_pressed_start_timer >= self.key_pressed_cooldown:
            self.key_pressed_start_timer = current_time

            if cfg.KEY_DL in inputs:
                self.test_character.move(cfg.MV_DL, self.camera_orientation)
                inputs.remove(cfg.KEY_DL)
            elif cfg.KEY_DR in inputs:
                self.test_character.move(cfg.MV_DR, self.camera_orientation)
                inputs.remove(cfg.KEY_DR)
            elif cfg.KEY_UR in inputs:
                self.test_character.move(cfg.MV_UR, self.camera_orientation)
                inputs.remove(cfg.KEY_UR)
            elif cfg.KEY_UL in inputs:
                self.test_character.move(cfg.MV_UL, self.camera_orientation)
                inputs.remove(cfg.KEY_UL)
            elif cfg.KEY_CAMERA_CLOCKWISE in inputs:
                camera_id = cfg.CAMERA_ORIENTATIONS.index(self.camera_orientation)
                camera_id = (camera_id + 1) % len(cfg.CAMERA_ORIENTATIONS)
                self.camera_orientation = cfg.CAMERA_ORIENTATIONS[camera_id]
                inputs.remove(cfg.KEY_CAMERA_CLOCKWISE)
            elif cfg.KEY_CAMERA_COUNTERCLOCKWISE in inputs:
                camera_id = cfg.CAMERA_ORIENTATIONS.index(self.camera_orientation)
                camera_id -= 1
                if camera_id < 0:
                    camera_id = len(cfg.CAMERA_ORIENTATIONS) - 1
                self.camera_orientation = cfg.CAMERA_ORIENTATIONS[camera_id]
                inputs.remove(cfg.KEY_CAMERA_COUNTERCLOCKWISE)
            elif cfg.KEY_QUIT in inputs:
                pygame.quit()
                sys.exit()

    def run(self) -> None:
        keys_pressed = []
        while True:
            self.screen.fill(cfg.BACKGROUND_COLOR_NAME)

            # Run game loop here before display update
            self.display_level(self.camera_orientation)

            pygame.display.update()
            self.clock.tick(cfg.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    keys_pressed.append(event.key)
            self.handle_input(keys_pressed)
