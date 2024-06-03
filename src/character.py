import sys
import pygame
import src.config as cfg
import src.support as sup
import src.tile_set as tile_set


class Character(pygame.sprite.Sprite):
    def __init__(self, groups: tuple, char_type: str, coord: tuple, orientation: str=cfg.CHARACTER_SW) -> None:
        super().__init__()
        for group in groups:
            self.add(group)

        self.char_type = char_type

        # x,y,z are always the coordinates of the character in the default (North) camera orientation
        self.coord_x = coord[0]
        self.coord_y = coord[1]
        # coord_z is equal to the map_z the character is standing on top of
        self.coord_z = coord[2]

        self.orientation = orientation

        self.tile_set = tile_set.TileSet(cfg.TILE_CHARACTER, cfg.CHARACTER_TEST)

        self.idle_anim_curr_frame = 0
        self.idle_animations = {
            cfg.CAMERA_NORTH: {
                cfg.CHARACTER_SW: [],
                cfg.CHARACTER_SE: [],
                cfg.CHARACTER_NE: [],
                cfg.CHARACTER_NW: []
            },
            cfg.CAMERA_WEST: {
                cfg.CHARACTER_SW: [],
                cfg.CHARACTER_SE: [],
                cfg.CHARACTER_NE: [],
                cfg.CHARACTER_NW: []
            },
            cfg.CAMERA_EAST: {
                cfg.CHARACTER_SW: [],
                cfg.CHARACTER_SE: [],
                cfg.CHARACTER_NE: [],
                cfg.CHARACTER_NW: []
            },
            cfg.CAMERA_SOUTH: {
                cfg.CHARACTER_SW: [],
                cfg.CHARACTER_SE: [],
                cfg.CHARACTER_NE: [],
                cfg.CHARACTER_NW: []
            },
        }

        self.load_animation_frames()

    def load_animation_frames(self) -> None:
        for camera_orientation in cfg.CAMERA_ORIENTATIONS:
            for i in range(cfg.CTEST_IDLE_FRAMES):
                self.idle_animations[camera_orientation][cfg.CHARACTER_SW].append(
                    self.tile_set.get_sprite_image(cfg.CTEST_IDLE_SW_SPRITE_ID + i, camera_orientation)
                )
                self.idle_animations[camera_orientation][cfg.CHARACTER_SE].append(
                    self.tile_set.get_sprite_image(cfg.CTEST_IDLE_SE_SPRITE_ID + i, camera_orientation)
                )
                self.idle_animations[camera_orientation][cfg.CHARACTER_NE].append(
                    self.tile_set.get_sprite_image(cfg.CTEST_IDLE_NE_SPRITE_ID + i, camera_orientation)
                )
                self.idle_animations[camera_orientation][cfg.CHARACTER_NW].append(
                    self.tile_set.get_sprite_image(cfg.CTEST_IDLE_NW_SPRITE_ID + i, camera_orientation)
                )

    def get_display_sprite(self, camera_orientation) -> pygame.Surface:
        if camera_orientation not in cfg.CAMERA_ORIENTATIONS:
            print(cfg.UNKNOWN_CAMERA_ORIENTATION, ':', camera_orientation, file=sys.stderr, flush=True)
            camera_orientation = cfg.CAMERA_NORTH

        return self.idle_animations[camera_orientation][self.orientation][self.idle_anim_curr_frame]

    # Uses standard character coord (north view), returns x,y,z in context of the specified camera orientation
    def get_orientation_coord(self, camera_orientation: str) -> tuple:
        if camera_orientation == cfg.CAMERA_WEST:
            x = cfg.MAP_WIDTH - 1 - self.coord_y
            y = self.coord_x
        elif camera_orientation == cfg.CAMERA_EAST:
            x = self.coord_y
            y = cfg.MAP_LENGTH - 1 - self.coord_x
        elif camera_orientation == cfg.CAMERA_SOUTH:
            x = cfg.MAP_WIDTH - 1 - self.coord_x
            y = cfg.MAP_LENGTH - 1 - self.coord_y
        else:
            if camera_orientation != cfg.CAMERA_NORTH:
                print(cfg.UNKNOWN_CAMERA_ORIENTATION, ':', camera_orientation, file=sys.stderr, flush=True)
            x = self.coord_x
            y = self.coord_y

        return x, y, self.coord_z

    # Provides the pygame.Rect at the coordinates on the screen where the character is currently displayed
    def get_rectangle(self, camera_orientation: str) -> pygame.Rect:
        return sup.get_sprite_rect(tuple(self.get_orientation_coord(camera_orientation)), True)

    # Coordinates received are the tile x,y,z in context of the current camera rotation
    # Player coordinates are adjusted to the x,y,z in context of the current camera rotation
    def is_behind_tile(self, tile_coord: tuple, camera_orientation: str) -> bool:
        if len(tile_coord) != 3:
            raise ValueError(cfg.INCORRECT_COORD_FORMAT + ' : ' + tile_coord)

        t_x = tile_coord[0]
        t_y = tile_coord[1]
        t_z = tile_coord[2]
        c_x, c_y, c_z = self.get_orientation_coord(camera_orientation)
        player_height_diff = t_z - c_z
        tile_rect = sup.get_sprite_rect(tile_coord)
        player_rect = self.get_rectangle(camera_orientation)

        if (player_height_diff >= 0
                and t_x >= c_x
                and t_y >= c_y
                and tile_rect.colliderect(player_rect)):
            return True
        else:
            return False

    # Coordinates received are the tile x,y,z in context of the current camera rotation
    # Player coordinates are adjusted to the x,y,z in context of the current camera rotation
    def is_character_behind_tile(self, tile_coord: tuple, camera_orientation: str) -> bool:
        if len(tile_coord) != 3:
            raise ValueError(cfg.INCORRECT_COORD_FORMAT + ' : ' + tile_coord)

        t_x = tile_coord[0]
        t_y = tile_coord[1]
        t_z = tile_coord[2]
        c_x, c_y, c_z = self.get_orientation_coord(camera_orientation)
        player_height_diff = t_z - c_z
        tile_rect = sup.get_sprite_rect(tile_coord)
        player_rect = sup.get_sprite_rect((c_x, c_y, c_z), True)

        if (player_height_diff >= 0
                and t_x >= c_x
                and t_y >= c_y
                and tile_rect.colliderect(player_rect)):
            return True
        else:
            return False

    def move(self, direction: str, camera_orientation: str) -> None:
        if direction not in cfg.MV_DIRECTIONS:
            raise ValueError(cfg.UNKNOWN_MOVE_DIRECTION + ':' + direction)
        if camera_orientation not in cfg.CAMERA_ORIENTATIONS:
            print(cfg.UNKNOWN_CAMERA_ORIENTATION, ':', camera_orientation, file=sys.stderr, flush=True)
            camera_orientation = cfg.CAMERA_NORTH

        offset_dict = {
            cfg.MV_DL: {
                cfg.CAMERA_NORTH: (0, 1),
                cfg.CAMERA_WEST: (1, 0),
                cfg.CAMERA_SOUTH: (0, -1),
                cfg.CAMERA_EAST: (-1, 0)
            },
            cfg.MV_DR: {
                cfg.CAMERA_NORTH: (1, 0),
                cfg.CAMERA_WEST: (0, -1),
                cfg.CAMERA_SOUTH: (-1, 0),
                cfg.CAMERA_EAST: (0, 1)
            },
            cfg.MV_UR: {
                cfg.CAMERA_NORTH: (0, -1),
                cfg.CAMERA_WEST: (-1, 0),
                cfg.CAMERA_SOUTH: (0, 1),
                cfg.CAMERA_EAST: (1, 0)
            },
            cfg.MV_UL: {
                cfg.CAMERA_NORTH: (-1, 0),
                cfg.CAMERA_WEST: (0, 1),
                cfg.CAMERA_SOUTH: (1, 0),
                cfg.CAMERA_EAST: (0, -1)
            }
        }

        direction_dict = offset_dict.get(direction)
        if direction_dict is None:
            raise NotImplementedError(cfg.NOT_IMPLEMENTED_MOVE_DIRECTION + ':' + direction)
        else:
            x = self.coord_x + direction_dict[camera_orientation][0]
            y = self.coord_y + direction_dict[camera_orientation][1]
            out_of_bounds = (x < 0
                             or x >= cfg.MAP_WIDTH
                             or y < 0
                             or y >= cfg.MAP_LENGTH)
            if not out_of_bounds:
                self.coord_x = x
                self.coord_y = y
