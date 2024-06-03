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

    # Takes in tile_coord in context of the camera_orientation, returns the correct sprite_id from the unmodified
    # (north oriented) default map
    def get_orientation_tile_sprite_id(self, tile_coord: tuple) -> int:
        if self.camera_orientation == cfg.CAMERA_WEST:
            sprite_id = self.map[tile_coord[2]][cfg.MAP_LENGTH - 1 - tile_coord[0]][tile_coord[1]]
        elif self.camera_orientation == cfg.CAMERA_EAST:
            sprite_id = self.map[tile_coord[2]][tile_coord[0]][cfg.MAP_WIDTH - 1 - tile_coord[1]]
        elif self.camera_orientation == cfg.CAMERA_SOUTH:
            sprite_id = self.map[tile_coord[2]][cfg.MAP_LENGTH - 1 - tile_coord[1]][cfg.MAP_WIDTH - 1 - tile_coord[0]]
        else:
            if self.camera_orientation != cfg.CAMERA_NORTH:
                print(cfg.UNKNOWN_CAMERA_ORIENTATION, ':', self.camera_orientation, file=sys.stderr, flush=True)
            sprite_id = self.map[tile_coord[2]][tile_coord[1]][tile_coord[0]]

        return int(sprite_id)

    def display_level(self) -> None:
        for map_x in range(cfg.MAP_WIDTH):
            for map_y in range(cfg.MAP_LENGTH):
                for map_z in range(len(self.map)):
                    if self.camera_orientation not in cfg.CAMERA_ORIENTATIONS:
                        print(cfg.UNKNOWN_CAMERA_ORIENTATION, ':', self.camera_orientation, file=sys.stderr, flush=True)
                        self.camera_orientation = cfg.CAMERA_NORTH

                    sprite_id = self.get_orientation_tile_sprite_id((map_x, map_y, map_z))
                    player_x, player_y, player_z = self.test_character.get_orientation_coord(self.camera_orientation)
                    if sprite_id != -1:
                        sprite = tile_set.TERRAIN_TILE_SET.get_sprite_image(sprite_id, self.camera_orientation)
                        # Make a tile translucent to reveal character behind
                        if self.test_character.is_character_behind_tile((map_x, map_y, map_z),
                                                                        self.camera_orientation):
                            sprite.set_alpha(128)
                        self.screen.blit(sprite, sup.get_sprite_rect((map_x, map_y, map_z)))

                    # Draws a character at its proper coordinates
                    # Redraws a character if a tile behind it but higher hides the previous character drawing
                    if player_x == map_x and player_y == map_y and player_z == map_z:
                        character_ground_tile_id = self.get_orientation_tile_sprite_id((map_x, map_y, map_z - 1))
                        is_on_stairs = character_ground_tile_id in cfg.TILE_STAIRS_SLOPES
                        character_sprite = self.test_character.get_display_sprite(self.camera_orientation)
                        character_rect = self.test_character.get_rectangle(self.camera_orientation, is_on_stairs)
                        self.screen.blit(character_sprite, character_rect)

    # Computes the coord of the selected character according to the camera orientation and movement direction.
    # Checks if the movement is valid (not out of bounds, no collision with terrain, use of stairs/slopes).
    # If appropriate, moves the character by the corresponding offsets of normalized (North) x,y,z
    def move_selected_character(self, direction: str):
        char_x = self.test_character.coord_x
        char_y = self.test_character.coord_y
        char_z = self.test_character.coord_z

        # Compute normalized (x, y) offset in regard to the camera orientation and the movement direction
        direction_dict = cfg.MV_OFFSET_DICT.get(direction)
        if direction_dict is None:
            raise NotImplementedError(cfg.NOT_IMPLEMENTED_MOVE_DIRECTION + ':' + direction)
        x_offset = direction_dict[self.camera_orientation][0]
        y_offset = direction_dict[self.camera_orientation][1]
        z_offset = 0
        # Compute new normalized (x, y) coordinates of the Character
        new_x = char_x + x_offset
        new_y = char_y + y_offset

        # Check if movement is valid on the current map
        out_of_bounds = (new_x < 0
                         or new_x >= cfg.MAP_WIDTH
                         or new_y < 0
                         or new_y >= cfg.MAP_LENGTH)
        if not out_of_bounds:
            collide_tile_id = int(self.map[char_z][new_y][new_x])
            # Will the player collide with a tile on the same Z as them
            if collide_tile_id != -1:
                # Is this tile stairs or a slope
                if collide_tile_id in cfg.TILE_STAIRS_SLOPES:
                    # Move up a level
                    z_offset += 1
                    self.test_character.move(x_offset, y_offset, z_offset)
                else:
                    # Collision with terrain that can't be crossed, ignore move command
                    pass
            else:
                curr_ground_tile = int(self.map[char_z - 1][char_y][char_x])
                next_ground_tile_id = int(self.map[char_z - 1][new_y][new_x])
                # Will the player stand on solid ground
                if (next_ground_tile_id == 0
                        or next_ground_tile_id in cfg.TILE_STAIRS_SLOPES):
                    # Stay on the same level
                    self.test_character.move(x_offset, y_offset, z_offset)
                else:
                    # Is the player currently on stairs or slope
                    if curr_ground_tile in cfg.TILE_STAIRS_SLOPES:
                        # Move down a level
                        z_offset -= 1
                        self.test_character.move(x_offset, y_offset, z_offset)
                    else:
                        # Can't jump off of cliffs, ignore move command
                        pass
        else:
            # Out of bounds, ignore move command
            pass

    def handle_input(self, inputs: list) -> None:
        current_time = pygame.time.get_ticks()
        if current_time - self.key_pressed_start_timer >= self.key_pressed_cooldown:
            self.key_pressed_start_timer = current_time

            if cfg.KEY_DL in inputs:
                self.move_selected_character(cfg.MV_DL)
                inputs.remove(cfg.KEY_DL)
            elif cfg.KEY_DR in inputs:
                self.move_selected_character(cfg.MV_DR)
                inputs.remove(cfg.KEY_DR)
            elif cfg.KEY_UR in inputs:
                self.move_selected_character(cfg.MV_UR)
                inputs.remove(cfg.KEY_UR)
            elif cfg.KEY_UL in inputs:
                self.move_selected_character(cfg.MV_UL)
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
            self.display_level()

            pygame.display.update()
            self.clock.tick(cfg.FPS)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    keys_pressed.append(event.key)
            self.handle_input(keys_pressed)
