import pygame
from .tile import Tile
import random

class Water(Tile):


    noise_texture = pygame.Surface((16, 16))
    for x in range(16):
        for y in range(16):
            c = random.randint(200, 255)
            col = (c, c, c)
            noise_texture.set_at((x, y), col)

    def __init__(self, *tile_args) -> None:
        super().__init__(*tile_args)
        self.color = (0, 75, 200)
        self.use_noise = False
