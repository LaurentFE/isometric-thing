import pygame
import src.config as cfg


class TileSet:
    def __init__(self, tile_type: str, type_label: str=None) -> None:
        super().__init__()

        self.images = {}
        self.sprites = {}

        if tile_type in cfg.TILE_TYPES:
            for orientation in cfg.CAMERA_ORIENTATIONS:
                if tile_type == cfg.TILE_CHARACTER:
                    if type_label is not None and type_label in cfg.CHARACTER_TYPES:
                        self.file = f'{cfg.GRAPHICS_FOLDER}{tile_type}/{type_label}/{type_label}{cfg.SPRITE_SIZE}_{orientation}{cfg.GRAPHICS_EXTENSION}'
                    else:
                        raise ValueError(cfg.UNKNOWN_CHARACTER_TYPE)
                else:
                    self.file = f'{cfg.GRAPHICS_FOLDER}{tile_type}/{tile_type}{cfg.SPRITE_SIZE}_{orientation}{cfg.GRAPHICS_EXTENSION}'
                self.images[orientation] = pygame.image.load(self.file)
                self.rect = self.images[orientation].get_rect()

                sprite_width = cfg.SPRITE_SIZE
                sprite_height = cfg.SPRITE_SIZE
                sprites_per_row = self.rect.width // cfg.SPRITE_SIZE
                sprite_rows = self.rect.height // cfg.SPRITE_SIZE

                oriented_sprites = {}
                for i in range(sprite_rows * sprites_per_row):
                    x = (i % sprites_per_row) * cfg.SPRITE_SIZE
                    y = (i // sprites_per_row) * cfg.SPRITE_SIZE
                    oriented_sprites[i] = self.images[orientation].subsurface(
                        (x, y, sprite_width, sprite_height)
                    ).convert_alpha()

                self.sprites[orientation] = oriented_sprites
        else:
            raise ValueError(cfg.UNKNOWN_TILE_TYPE)

    def get_sprite_image(self, sprite_id: int, orientation: str):
        return self.sprites[orientation][sprite_id].copy()


# Global TileSet instances, they MUST be instantiated in Game __init__
# Characters will get their own tileset as an attribute
TERRAIN_TILE_SET = None
