import pygame
from .tile import Tile

class Water(Tile):

    def __init__(self, *tile_args) -> None:
        super().__init__(*tile_args)
        self.color = (0, 75, 200)
