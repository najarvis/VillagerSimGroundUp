import pygame
from .tile import Tile

class Dirt(Tile):

    def __init__(self, coord: pygame.Vector2, size: int | tuple[int, int]) -> None:
        super().__init__(coord, size)
        self.color = (115,118,83)
