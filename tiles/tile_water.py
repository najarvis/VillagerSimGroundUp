from tile import Tile
import pygame

class Water(Tile):

    def __init__(self) -> None:
        super().__init__()
        self.color = (0, 75, 200)
