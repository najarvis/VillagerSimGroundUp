
import math
import random
import pygame

from procgen.procgen.noise import perlin2D

from globals import TILE_SIZE, WORLD_SIZE, CHUNK_SIZE
from tiles.tile import Tile
from tiles.tile_dirt import Dirt
from tiles.tile_grass import Grass
from tiles.tile_sand import Sand
from tiles.tile_water import Water
from tiles.tile_stone import Stone
from tiles.tile_snow import Snow
from tile_chunk import TileChunk

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

        self.chunks = [] # list[list[TileChunk]]
        
        self.generate()
        self.render_chunks()

    def generate(self) -> None:
        """Generates new terrain. Overwrites previous terrain."""

        # rand_x and rand_y are effectively the "seed" for the noise, but 
        # are more accurately the position from which we start looking at
        # the noise function
        rand_x = random.random()
        rand_y = random.random()
        terrain_scale = 8.0 # Higher = more fine detail for the base terrain
        perturb_scale = 16.0 # How detailed the perturbation is
        p_vals = []

        center = pygame.Vector2(WORLD_SIZE[0] / 2, WORLD_SIZE[1] / 2)

        for x in range(WORLD_SIZE[0]):
            for y in range(WORLD_SIZE[1]):
                # Perturbing will adjust what coordinate we're looking at in the noise function
                perturb_amount = perlin2D(x * perturb_scale / WORLD_SIZE[0], y * perturb_scale / WORLD_SIZE[1])
                perturb_amount /= 16.0 # Increase this number to reduce the magnitude of the perturbation 
                # perturb_amount *= 0.125 # Alternate way to do above. Not sure which makes more sense

                angle = math.pi * 2 * perturb_amount

                perturb_x = math.cos(angle)
                perturb_y = math.sin(angle)

                # perlin2D returns values in the -0.5 to 0.5 range. Add 1 to make that 0.5 to 1.5
                p_val = perlin2D((x / WORLD_SIZE[0]) * terrain_scale + rand_x + perturb_x, 
                                 (y / WORLD_SIZE[1]) * terrain_scale + rand_y + perturb_y
                        ) + 1.0

                # 0.33 to 1.0 now
                p_val /= 1.5
                
                # Distance from the center, divided by the distance to the closest edge. Will
                # return 1 for coordinates on the midpoints of edges and > 1 for values closer to the corners
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

        # 2D array of TileChunk instances
        self.chunks = []

        # This quad nested for loop will hit the inner code once for each tile in the world
        for x in range(WORLD_SIZE[0] // CHUNK_SIZE[0]):
            chunk_row = []
            for y in range(WORLD_SIZE[1] // CHUNK_SIZE[1]):
                # The chunks are surfaces we pre-render to speed up drawing and updating the tiles each frame
                new_chunk = TileChunk(pygame.Vector2(x, y))
                chunk_surf = new_chunk.get_chunk_surf()

                for tile_x in range(x * CHUNK_SIZE[0], x * CHUNK_SIZE[0] + CHUNK_SIZE[0]):
                    for tile_y in range(y * CHUNK_SIZE[1], y * CHUNK_SIZE[1] + CHUNK_SIZE[1]):
                        # If we try to draw a tile that's in the middle of the world on a chunk without wrapping
                        # its position it will draw off the chunk
                        wrap_pos_x = tile_x % CHUNK_SIZE[0]
                        wrap_pos_y = tile_y % CHUNK_SIZE[1]
                        draw_pos = pygame.Vector2(wrap_pos_x * TILE_SIZE[0], wrap_pos_y * TILE_SIZE[1])

                        self.tiles[tile_x][tile_y].draw(chunk_surf, draw_pos)

                chunk_row.append(new_chunk)
            self.chunks.append(chunk_row)

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the whole world, by going through each chunk"""

        for chunk_row in self.chunks:
            for chunk in chunk_row:
                chunk.draw(surface)
