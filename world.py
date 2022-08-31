
import random
import pygame

from procgen.procgen.noise import perlin2D

from globals import TILE_SIZE, WORLD_SIZE
from tiles.tile import Tile
from tiles.tile_dirt import Dirt
from tiles.tile_grass import Grass
from tiles.tile_sand import Sand
from tiles.tile_water import Water
from tiles.tile_stone import Stone
from tiles.tile_snow import Snow

def easeInExpo(x: float) -> float:
    if x == 0:
        return 0

    return pow(2, 10 * min(x, 1) - 10)

class World():
    """Singleton that holds the state of the game world.
    
    Generates random terrain, stores and renders the tiles and chunks.
    """

    def __init__(self):
        self.tile_size = TILE_SIZE[0]
        self.tiles = [[None \
            for _ in range(WORLD_SIZE[0])] 
            for _ in range(WORLD_SIZE[1])]

        self.chunk_surfaces = [] # list[tuple[(pygame.Surface, coordinate)]]
        self.chunk_size = 16
        
        self.generate()
        self.render_chunks()

    def generate(self) -> None:
        """Generates new terrain. Overwrites previous terrain."""

        # rand_x and rand_y are effectively the "seed" for the noise, but 
        # are more accurately the position from which we start looking at
        # the noise function
        rand_x = random.random()
        rand_y = random.random()
        scale = 8.0 # Higher = more fine detail
        p_vals = []

        center = pygame.Vector2(WORLD_SIZE[0] / 2, WORLD_SIZE[1] / 2)

        for x in range(WORLD_SIZE[0]):
            for y in range(WORLD_SIZE[1]):
                # perlin2D returns values in the -0.5 to 0.5 range. Add 1 to make that 0.5 to 1.0
                p_val = perlin2D((x / WORLD_SIZE[0]) * scale + rand_x, 
                                 (y / WORLD_SIZE[1]) * scale + rand_y
                        ) + 1.0

                # 0.33 to 1.0 now
                p_val /= 1.5
                
                # Distance from the center to the closest edge
                radial_value = pygame.Vector2(x, y).distance_to(center) / min(center.x, center.y)

                # don't remove much near the middle, only on the edges
                p_val -= easeInExpo(radial_value)

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

    def render_chunks(self) -> None:
        """Instead of rendering every tile every frame, we can render the tiles to chunks, and then draw whole
        chunks at a time. If a tile needs to be updated only the chunk needs to be re-rendered.
        """

        self.chunk_surfaces = []

        for x in range(WORLD_SIZE[0] // self.chunk_size):
            for y in range(WORLD_SIZE[1] // self.chunk_size):
                new_surface = pygame.Surface((TILE_SIZE[0] * self.chunk_size, TILE_SIZE[1] * self.chunk_size))

                for tile_x in range(x * self.chunk_size, x * self.chunk_size + self.chunk_size):
                    for tile_y in range(y * self.chunk_size, y * self.chunk_size + self.chunk_size):
                        wrap_pos_x = tile_x % self.chunk_size
                        wrap_pos_y = tile_y % self.chunk_size
                        draw_pos = pygame.Vector2(wrap_pos_x * TILE_SIZE[0], wrap_pos_y * TILE_SIZE[1])
                        self.tiles[tile_x][tile_y].draw(new_surface, draw_pos)

                self.chunk_surfaces.append((new_surface, (x, y)))

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the whole world, by going through each chunk"""

        for chunk_surf, coord in self.chunk_surfaces:
            surface.blit(chunk_surf, (coord[0] * TILE_SIZE[0] * self.chunk_size, coord[1] * TILE_SIZE[1] * self.chunk_size))


