import pygame
from tile import Tile

class World():

    def __init__(self, world_size) -> None:
        tile_size = 32
        self.tiles = tiles = [[Tile(pygame.Vector2(x * tile_size, y * tile_size), tile_size) \
            for x in range(world_size[0])] 
            for y in range(world_size[1])]

    def draw(self, surface):
        for tile_row in self.tiles:
            for tile in tile_row:
                tile.draw(surface)



