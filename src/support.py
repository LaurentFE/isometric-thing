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


# Coordinates received are the tile x,y,z in context of the current camera rotation
def get_sprite_rect(sprite_coord: tuple) -> pygame.Rect:
    if len(sprite_coord) != 3:
        raise ValueError(cfg.INCORRECT_COORD_FORMAT + ' : ' + sprite_coord)

    height_adjusted_x = sprite_coord[0] - sprite_coord[2]
    height_adjusted_y = sprite_coord[1] - sprite_coord[2]
    display_x = cfg.TILE0_X + cfg.TILE_X_OFFSET * (height_adjusted_x - height_adjusted_y)
    display_y = cfg.TILE0_Y + cfg.TILE_Y_OFFSET * (height_adjusted_x + height_adjusted_y)

    return pygame.Rect(display_x, display_y, cfg.SPRITE_SIZE, cfg.SPRITE_SIZE)
