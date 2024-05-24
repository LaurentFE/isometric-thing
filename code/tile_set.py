import pygame
import code.config as cfg


class TileSet:
    def __init__(self, tile_type):
        super().__init__()

        if tile_type in cfg.TILE_TYPES:
            self.file = f'{cfg.GRAPHICS_FOLDER}{tile_type}/{tile_type}{cfg.GRAPHICS_EXTENSION}'
            self.image = pygame.image.load(self.file)
            self.rec = self.image.get_rect()

            pygame.display.get_surface().blit(self.image, (0, 0))

            self.sprite_width = cfg.SPRITE_SIZE
            self.sprite_height = cfg.SPRITE_SIZE
            self.sprites_per_row = self.rec.width // cfg.SPRITE_SIZE
            self.sprite_rows = self.rec.height // cfg.SPRITE_SIZE

            self.sprites = {}
            for i in range(self.sprite_rows * self.sprites_per_row):
                x = (i % self.sprites_per_row) * cfg.SPRITE_SIZE
                y = (i // self.sprites_per_row) * cfg.SPRITE_SIZE
                self.sprites[i] = self.image.subsurface((x, y, self.sprite_width, self.sprite_height)).convert_alpha()
        else:
            raise ValueError(cfg.UNKNOWN_TILE_TYPE)

    def get_sprite_image(self, sprite_id: int):
        return self.sprites[sprite_id].copy()


# Global TileSet instances, they MUST be instantiated in Game __init__
TERRAIN_TILE_SET = None
