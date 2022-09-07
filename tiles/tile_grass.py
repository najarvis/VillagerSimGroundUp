import pygame
from .tile import Tile

class Grass(Tile):

    def __init__(self, *tile_args) -> None:
        super().__init__(*tile_args)
        self.color = (47, 137, 57)
