import pygame
from .tile import Tile

class Dirt(Tile):

    def __init__(self, *tile_args) -> None:
        super().__init__(*tile_args)
        self.color = (115,118,83)
