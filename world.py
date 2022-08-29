import pygame
from procgen.procgen.noise import perlin2D
import random

from tiles.tile import Tile
from tiles.tile_dirt import Dirt
from tiles.tile_grass import Grass
from tiles.tile_sand import Sand
from tiles.tile_water import Water
from tiles.tile_stone import Stone
from tiles.tile_snow import Snow


class World():

    def __init__(self, world_size: tuple[int, int]) -> None:
        self.tile_size = 32
        self.world_size = world_size
        self.tiles = [[None \
            for x in range(world_size[0])] 
            for y in range(world_size[1])]
        
        self.generate()
        
    def generate(self):
        rand_x = random.random()
        rand_y = random.random()

        p_vals = []

        for x in range(self.world_size[0]):
            for y in range(self.world_size[1]):
                p_val = perlin2D(x + rand_x, y + rand_y) + 0.5
                p_vals.append(p_val)
                if p_val < 0.5:
                    print("WATER!")
                    self.tiles[x][y] = Water(pygame.Vector2(x * self.tile_size, y * self.tile_size), self.tile_size)
                else:
                    self.tiles[x][y] = Dirt(pygame.Vector2(x * self.tile_size, y * self.tile_size), self.tile_size)

        print(min(p_vals), max(p_vals))

    def draw(self, surface: pygame.Surface) -> None:
        for tile_row in self.tiles:
            for tile in tile_row:
                tile.draw(surface)



