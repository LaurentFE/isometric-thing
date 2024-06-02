import pygame
import sys
import src.config as cfg
from csv import reader


# Reads a csv file as a map layout
# There is one csv file per layer of a given map, corresponding to each Z coordinate on the map
def import_csv_layout(path: str, ignore_non_existing_file: bool=False) -> list:
    layout = []
    try:
        with open(path) as file:
            parsed = reader(file, delimiter=',')
            for row in parsed:
                layout.append(list(row))
    except FileNotFoundError:
        if not ignore_non_existing_file:
            print(f'FileNotFoundError: No such file or directory: \'{path}\'', file=sys.stderr)
            pygame.quit()
            sys.exit()

    return layout


# Takes in tile_coord in context of the camera_orientation, returns the correct sprite_id from the unmodified
# (north oriented) default sprite_map
def get_orientation_tile_sprite_id(sprite_map: list, tile_coord: tuple, camera_orientation: str) -> int:
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
def get_sprite_rect(sprite_coord: tuple, is_character: bool=False) -> pygame.Rect:
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
