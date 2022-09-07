import pygame
from .tile import Tile

class Sand(Tile):

    def __init__(self, *tile_args) -> None:
        super().__init__(*tile_args)
        self.color = (194, 178, 128)