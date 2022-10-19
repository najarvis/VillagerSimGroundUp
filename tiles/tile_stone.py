import pygame
from .tile import Tile

class Stone(Tile):

    def __init__(self, *tile_args) -> None:
        super().__init__(*tile_args)
        self.color = (111, 122, 132 )
        self.use_noise = False
