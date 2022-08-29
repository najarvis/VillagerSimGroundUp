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
        self.tile_size = 8
        self.world_size = world_size
        self.tiles = [[None \
            for x in range(world_size[0])] 
            for y in range(world_size[1])]
        
        self.generate()
        
    def generate(self):
        rand_x = random.random()
        rand_y = random.random()
        scale = 4.0 # Higher = more fine detail
        p_vals = []

        for x in range(self.world_size[0]):
            for y in range(self.world_size[1]):
                p_val = perlin2D((x / self.world_size[0]) * scale + rand_x, 
                                 (y / self.world_size[1]) * scale + rand_y
                        ) + 0.5
                
                p_vals.append(p_val)
                tile_type = None
                if p_val < 0.4:
                    tile_type = Water
                elif p_val < 0.45:
                    tile_type = Sand
                elif p_val < 0.55:
                    tile_type = Dirt
                elif p_val < 0.7:
                    tile_type = Grass
                elif p_val < 0.9:
                    tile_type = Stone
                else:
                    tile_type = Snow
                    
                self.tiles[x][y] = tile_type(pygame.Vector2(x * self.tile_size, y * self.tile_size), self.tile_size)
                

    def draw(self, surface: pygame.Surface) -> None:
        for tile_row in self.tiles:
            for tile in tile_row:
                tile.draw(surface)



