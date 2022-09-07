import pygame
from .tile import Tile

class Snow(Tile):

    def __init__(self, *tile_args) -> None:
        super().__init__(*tile_args)
        self.color = (255, 255, 255)
