import math
import random
import pygame

import time
from camera import Camera

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

from world_generation.noise import worley_noise, worley_noise_val

def easeInExpo(x: float) -> float:
    if x == 0:
        return 0

    return pow(2, 10 * min(x, 1) - 10)

def noise2D(x: float, y: float) -> float:
    """perlin2D noise from 0-1"""
    return perlin2D(x, y) + 0.5

class World():
    """Singleton that holds the state of the game world.
    
    Generates random terrain, stores and renders the tiles and chunks.
    """

    def __init__(self):
        self.tile_size = TILE_SIZE[0]
        self.tiles = [[None \
            for _ in range(WORLD_SIZE[0])]
            for _ in range(WORLD_SIZE[1])]

        # Only store chunks, don't store tiles directly. 
        self.chunks = [] # list[list[TileChunk]]
        
        self.camera = Camera(pygame.Vector2(WORLD_SIZE[0] / 2, WORLD_SIZE[1] / 2))

        t0 = time.time()
        self.generate()
        t1 = time.time()
        self.render_chunks()
        t2 = time.time()

        print(f"Generation took {round(t1-t0,2)}s")
        print(f"Drawing chunks took {round(t2-t1,2)}s")

    def update(self, delta: float) -> None:
        pass

    @staticmethod
    def calculate_tile(height, humidity, temperature=1.0):
        """Determine a tile's type based on factors at a given location"""
        if height < 0.3:
            return Water
        elif height < 0.35:
            return Sand
        elif height < 0.8:
            if humidity < 0.3:
                return Stone
            if humidity < 0.6:
                return Dirt
            return Grass
        else:
            if humidity < 0.5:
                return Stone
            return Snow

    def generate(self) -> None:
        """Generates new terrain. Overwrites previous terrain."""

        # TODO: Different maps (height, temperature, humidity) should be defined
        # in their own classes, and combined in another class, and then the tiles 
        # are instanciated and added to the chunk here

        # rand_x and rand_y are effectively the "seed" for the noise, but 
        # are more accurately the position from which we start looking at
        # the noise function
        rand_x = random.uniform(0, 1000)
        rand_y = random.uniform(0, 1000)
        terrain_scale = 8.0 # Higher = more fine detail for the base terrain
        biome_scale = 4.0
        perturb_scale = 20.0 # How detailed the perturbation is
        perturb_range = 0.15 # How far away a coordinate can be offset by the perturbation

        worley_vec1 = pygame.Vector2(random.uniform(-1000, 1000), random.uniform(-1000, 1000))
        worley_vec2 = pygame.Vector2(random.uniform(-1000, 1000), random.uniform(-1000, 1000))

        center = pygame.Vector2(WORLD_SIZE[0] / 2, WORLD_SIZE[1] / 2)
        heights = []

        for x in range(WORLD_SIZE[0]):
            height_row = [0] * WORLD_SIZE[1]
            for y in range(WORLD_SIZE[1]):
                # Perturbing will adjust what coordinate we're looking at in the noise function
                # Add 3 octaves of noise for the perturbation. May be overkill but looks nice
                perturb_noise_coord = pygame.Vector2((x + rand_x) * perturb_scale / WORLD_SIZE[0],
                                                     (y + rand_y) * perturb_scale / WORLD_SIZE[1])
                perturb_amount = noise2D(*(perturb_noise_coord)) + \
                                 0.50 * noise2D(*(perturb_noise_coord * 2)) + \
                                 0.25 * noise2D(*(perturb_noise_coord * 4))
                perturb_amount /= (1 + 0.5 + 0.25) # Normalize range to [0, 1]

                # We create an offset by treating the noise value (perturb_amount) as a
                # random angle, then creating a vector pointing in that direction.
                angle = math.pi * 2 * perturb_amount
                perturb_x = math.cos(angle) * perturb_range
                perturb_y = math.sin(angle) * perturb_range

                # Add 3 octaves of noise for the height. Add the pertub coordinate to the noise coordinate.
                noise_coord = pygame.Vector2((x / WORLD_SIZE[0]) * terrain_scale + rand_x + perturb_x, 
                                             (y / WORLD_SIZE[1]) * terrain_scale + rand_y + perturb_y)
                p_val = noise2D(*noise_coord) + \
                        0.50 * noise2D(*(noise_coord * 2)) + \
                        0.25 * noise2D(*(noise_coord * 4))
                p_val /= (1 + 0.5 + 0.25) # Normalize range to [0, 1]

                # Add in some worley noise. Perturb to add variation to the straight lines of the texture
                worley_pos = pygame.Vector2(((x + perturb_x) % WORLD_SIZE[0]) / WORLD_SIZE[0], 
                                            ((y + perturb_y) % WORLD_SIZE[1]) / WORLD_SIZE[1])
                worley_dists = worley_noise(worley_pos, 4, 4, worley_vec1, worley_vec2)
                worley_val = worley_noise_val(worley_dists, [-1, 1])

                # 2/3 perlin noise and 1/3 worley noise
                h_val = p_val * 0.66 + worley_val * 0.33
                
                # Distance from the center, divided by the distance to the closest edge. Will
                # return 1 for coordinates on the midpoints of edges and > 1 for values closer to the corners
                radial_value = pygame.Vector2(x, y).distance_to(center) / min(center.x, center.y)

                # don't remove much near the middle, only on the edges
                height = h_val - easeInExpo(radial_value)
                height_row[y] = height
                
            heights.append(height_row)

        t0=time.time()
        World.thermal_erosion(heights, 2)
        print(f"Erosion took: {round(time.time()-t0, 2)}s")
        World.hydraulic_erosion(heights)

        print("Calculating humidity map")
        humidity_map = World.calculate_humidity_map(WORLD_SIZE, heights)
        print("Done")

        for x in range(WORLD_SIZE[0]):
            for y in range(WORLD_SIZE[1]):
                height = heights[x][y]
                fx, fy = x / WORLD_SIZE[0], y / WORLD_SIZE[1]
                # rel_height controls the extra shadow drawn on the tiles. The lower the value the darker [0, 1]
                # Adds a little bit of visual texture. No functional impact
                rel_height = 1.0

                tile_type = None

                humidity = 1.0 - (min(WORLD_SIZE[0] / 16, humidity_map[x][y]) / (WORLD_SIZE[0] / 16))
                tile_type = World.calculate_tile(height, humidity)
                if height < 0.3:
                    rel_height = max(0, height) / 0.3
                else:
                    rel_height = (height - 0.3) / 0.7
                    
                self.tiles[x][y] = tile_type(pygame.Vector2(x * self.tile_size, y * self.tile_size), self.tile_size, rel_height)

    @staticmethod
    def get_neighborhood(array, coord: pygame.Vector2) -> list:
        if len(array) == 0 or len(array[0]) == 0:
            return []

        return_arr = []

        for x_coord in range(int(max(0, coord.x-1)), int(min(len(array), coord.x+2))):
            for y_coord in range(int(max(0, coord.y-1)), int(min(len(array[0]), coord.y+2))):
                if x_coord == coord.x and y_coord == coord.y:
                    continue
                return_arr.append((x_coord, y_coord))
        return return_arr

    @staticmethod
    def thermal_erosion(height_map: list[list[float]], iterations: int) -> None:
        """Iterate over a height map and simulate thermal erosion. This involves
        reducing moving material from very steep areas to the surrounding areas.
        """

        T = 4 / WORLD_SIZE[0]
        for i in range(iterations):
            print(f"Thermal erosion iteration {i+1}")
            adjusted = False
            for row_y, row in enumerate(height_map):
                for row_x, height in enumerate(row):
                    neighbors = World.get_neighborhood(height_map, pygame.Vector2(row_x, row_y))
                    delta_total = 0
                    delta_max = 0
                    move_to_cells = []
                    for neighbor_coord in neighbors:
                        delta = height - height_map[neighbor_coord[1]][neighbor_coord[0]]
                        if delta > T:
                            delta_total += delta
                            delta_max = max(delta, delta_max)
                            move_to_cells.append((neighbor_coord, delta))
                            

                    for coord, dt in move_to_cells:
                        adjust = 0.05 * (delta_max - T) * (dt / delta_total)
                        height_map[coord[1]][coord[0]] += adjust
                        height_map[row_y][row_x] -= adjust
                        adjusted = True

            if not adjusted:
                break

    @staticmethod
    def hydraulic_erosion(array) -> None:
        NotImplemented

    @staticmethod
    def calculate_humidity_map(size: tuple[int, int], heights: list[list[float]]) -> list[list[float]]:
        """TODO: Not really working. Too 'blocky'"""

        # output will hold the distance to the closest water source for a given coordinate 
        output = [[1000 for _ in range(size[0])] for _ in range(size[1])]
        # queue contains a list of all possible tile coordinates
        queue = list((x, y) for x in range(size[0]) for y in range(size[1]))
        while len(queue) > 0:
            next_coord = queue.pop()
            height = heights[next_coord[0]][next_coord[1]]
            if height < 0.3:
                # heights are from 0-1 and less than 0.3 is How the game currently defines water
                output[next_coord[0]][next_coord[1]] = 0
            else:
                min_dist = 1000
                # This gets the coordinates of the 8 surrounding neighbors. Handles edges
                neighbors = neighbors = World.get_neighborhood(heights, pygame.Vector2(next_coord))
                for neighbor in neighbors:
                    min_dist = min(min_dist, output[neighbor[0]][neighbor[1]])
                    if min_dist == 0:
                        # If one of the neighboring distances is water, no need to look at the other tiles
                        break
                
                output[next_coord[0]][next_coord[1]] = min_dist + 1
        return output


    def render_chunks(self) -> None:
        """Instead of rendering every tile every frame, we can render the tiles to chunks, and then draw whole
        chunks at a time. If a tile needs to be updated only the chunk needs to be re-rendered.
        """

        # TODO: The individual tile rendering should be done on the chunk level.

        # 2D array of TileChunk instances
        self.chunks = []

        # This quad nested for loop will hit the inner code once for each tile in the world
        for x in range(WORLD_SIZE[0] // CHUNK_SIZE[0]):
            chunk_row = []
            for y in range(WORLD_SIZE[1] // CHUNK_SIZE[1]):
                # The chunks are surfaces we pre-render to speed up drawing and updating the tiles each frame
                new_chunk = TileChunk(pygame.Vector2(x * CHUNK_SIZE[0], y * CHUNK_SIZE[1]))
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
                chunk.draw(surface, self.camera)
