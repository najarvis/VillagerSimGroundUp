import chunk
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

from world_generation.noise import worley_noise, worley_noise_val, random1, random2, fBm_noise

def easeInExpo(x: float) -> float:
    if x == 0:
        return 0

    return pow(2, 10 * min(x, 1) - 10)

def noise2D(x: float, y: float) -> float:
    """perlin2D noise from 0-1"""
    return perlin2D(x, y) + 0.5

def timefunc(func):
    """Decorator that reports the execution time."""
  
    def wrap(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
          
        # print(f"{func.__name__} took {round(end-start, 3)}s")
        return result
    return wrap

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
        self.chunks = {} # list[list[TileChunk]]
        
        self.camera = Camera(pygame.Vector2(WORLD_SIZE[0] / 2, WORLD_SIZE[1] / 2))

        self.rand_seed_x = random.uniform(0, 1000)
        self.rand_seed_y = random.uniform(0, 1000)

        self.chunk_coords = {}
        self.edge_chunks = set()
        #self.generate()

        #self.render_chunks()

    def update(self, delta: float) -> None:
        looking_at_chunk = self.get_corresponding_chunk(self.camera.get_position())
        chunk_pos = (int(looking_at_chunk.x), int(looking_at_chunk.y))
        if chunk_pos not in self.chunks:
            self.generate_chunk(looking_at_chunk)
            
            top    = (chunk_pos[0], chunk_pos[1] + CHUNK_SIZE[1])
            bottom = (chunk_pos[0], chunk_pos[1] - CHUNK_SIZE[1])
            left   = (chunk_pos[0] - CHUNK_SIZE[0], chunk_pos[1])
            right  = (chunk_pos[0] + CHUNK_SIZE[0], chunk_pos[1])

            for pos in (top, bottom, left, right):
                if pos not in self.chunk_coords:
                    self.edge_chunks.add(pos)

        else:
            non_visible = set()
            while len(self.edge_chunks) > 0:
                new_pos = self.edge_chunks.pop()
                screen_coord = self.camera.world_to_screen((new_pos[0] + 8, new_pos[1] + 8))
                bounds_rect = pygame.Rect(0, 0, *CHUNK_SIZE)
                bounds_rect.w *= self.camera.scale
                bounds_rect.h *= self.camera.scale
                bounds_rect.topleft = screen_coord
                # Don't do the work of scaling an image if it won't be on the screen
                if not bounds_rect.colliderect(TileChunk.SCREEN_RECT):
                    # non_visible.add(new_pos)
                    continue
                
                self.generate_chunk(pygame.Vector2(new_pos))
                
                top    = (new_pos[0], new_pos[1] + CHUNK_SIZE[1])
                bottom = (new_pos[0], new_pos[1] - CHUNK_SIZE[1])
                left   = (new_pos[0] - CHUNK_SIZE[0], new_pos[1])
                right  = (new_pos[0] + CHUNK_SIZE[0], new_pos[1])

                for pos in (top, bottom, left, right):
                    if pos not in self.chunks:
                        non_visible.add(pos)

            self.edge_chunks = non_visible
        self.render_chunks()


    def generate(self) -> None:
        """Generates new terrain. Overwrites previous terrain."""

        # TODO: Different maps (height, temperature, humidity) should be defined
        # in their own classes, and combined in another class, and then the tiles 
        # are instanciated and added to the chunk here

        for x in range(5):
            for y in range(5):
                position = pygame.Vector2(x * CHUNK_SIZE[0], y * CHUNK_SIZE[1])
                self.generate_chunk(position)
                print(position)

    def generate_chunk(self, position):
        heights = self.generate_heightmap(position)
        humidity_map = [[0] * CHUNK_SIZE[0]] * CHUNK_SIZE[1]
        #humidity_map = World.calculate_humidity_map_ff(heights)
        chunk_tiles = self.generate_tiles(position, heights, humidity_map)
        self.chunks[(int(position.x), int(position.y))] = TileChunk(position, chunk_tiles, self)

    def get_corresponding_chunk(self, coord):
        chunk_x = (coord[0] // CHUNK_SIZE[0]) * CHUNK_SIZE[0]
        chunk_y = (coord[1] // CHUNK_SIZE[1]) * CHUNK_SIZE[1]
        return pygame.Vector2(chunk_x, chunk_y)

    @staticmethod
    def calculate_tile(height, humidity, temperature=1.0):
        """Determine a tile's type based on factors at a given location"""
        if height < 0.3:
            return Water
        elif height < 0.35:
            return Sand
        elif height < 0.8:
            if humidity < 0.4:
                return Stone
            if humidity < 0.5:
                return Dirt
            return Grass
        elif height < 0.9:
            if humidity < 0.8:
                return Stone
            return Snow
        else:
            if humidity < 0.3:
                return Stone
            return Snow

    @timefunc
    def generate_heightmap(self, position=(0, 0), chunk_size=CHUNK_SIZE, worley_vec1 = pygame.Vector2(127.5123, 247.124), worley_vec2=pygame.Vector2(523.216, 112.351)) -> list[list[float]]:
        # rand_x and rand_y are effectively the "seed" for the noise, but 
        # are more accurately the position from which we start looking at
        # the noise function
        rand_x = self.rand_seed_x
        rand_y = self.rand_seed_y
        terrain_scale = 8.0 # Higher = more fine detail for the base terrain
        perturb_scale = 20.0 # How detailed the perturbation is

        #worley_vec1 = pygame.Vector2(random.uniform(-1000, 1000), random.uniform(-1000, 1000))
        #worley_vec2 = pygame.Vector2(random.uniform(-1000, 1000), random.uniform(-1000, 1000))

        #center = pygame.Vector2(chunk_size[0] / 2, chunk_size[1] / 2)
        center = pygame.Vector2(WORLD_SIZE[0] / 2, WORLD_SIZE[1] / 2)
        heights = [[None for _ in range(chunk_size[0])] for _ in range(chunk_size[1])]

        for x_int in range(chunk_size[0]):
            for y_int in range(chunk_size[1]):
                x = float(x_int + position[0])
                y = float(y_int + position[1])
                # Perturbing will adjust what coordinate we're looking at in the noise function
                # Add 3 octaves of noise for the perturbation. May be overkill but looks nice
                perturb_noise_coord = pygame.Vector2((x + rand_x) * perturb_scale / WORLD_SIZE[0],
                                                     (y + rand_y) * perturb_scale / WORLD_SIZE[1])
                perturb_amount = noise2D(*(perturb_noise_coord)) + \
                                    0.50 * noise2D(*(perturb_noise_coord * 2)) + \
                                    0.25 * noise2D(*(perturb_noise_coord * 4))
                perturb_amount /= (1 + 0.5 + 0.25) # Normalize range to [0, 1]

                # How far away a coordinate can be offset by the perturbation
                perturb_range = fBm_noise(pygame.Vector2(x, y), 5, frequency=8) * 0.3

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

                large_scale_noise = noise2D(*(noise_coord / 16))
                p_val *= large_scale_noise

                # # Add in some worley noise. Perturb to add variation to the straight lines of the texture
                # worley_pos = pygame.Vector2(((x + perturb_x) % WORLD_SIZE[0]) / WORLD_SIZE[0], 
                #                             ((y + perturb_y) % WORLD_SIZE[1]) / WORLD_SIZE[1])
                # worley_dists = worley_noise(worley_pos, 4, 4, worley_vec1, worley_vec2)
                # worley_val = worley_noise_val(worley_dists, [-1, 1])

                # 2/3 perlin noise and 1/3 worley noise
                h_val = p_val #p_val * 0.66 + worley_val * 0.33
                
                # Distance from the center, divided by the distance to the closest edge. Will
                # return 1 for coordinates on the midpoints of edges and > 1 for values closer to the corners
                radial_value = pygame.Vector2(x, y).distance_to(center) / min(center.x, center.y)

                # don't remove much near the middle, only on the edges
                height = h_val - easeInExpo(radial_value)
                heights[y_int][x_int] = h_val

        return heights

    def generate_tiles(self, position, heights, humidity_map, chunk_size=CHUNK_SIZE):
        tiles = [[None for _ in range(chunk_size[0])] for _ in range(chunk_size[1])]
        for y in range(int(position[1]), int(position[1]) + chunk_size[1]):
            for x in range(int(position[0]), int(position[0]) + chunk_size[0]):
                height = heights[y % chunk_size[0]][x % chunk_size[1]]
                fx, fy = x / WORLD_SIZE[0], y / WORLD_SIZE[1]
                # rel_height controls the extra shadow drawn on the tiles. The lower the value the darker [0, 1]
                # Adds a little bit of visual texture. No functional impact
                rel_height = 1.0

                tile_type = None

                max_humidity_distance = WORLD_SIZE[0] / 10
                humidity = 1.0 - (min(max_humidity_distance, humidity_map[y % chunk_size[0]][x % chunk_size[1]]) / max_humidity_distance)
                humidity += fBm_noise(pygame.Vector2(fx, fy), 5, frequency=8.0)
                humidity /= 2.0
                tile_type = World.calculate_tile(height, humidity)
                if height < 0.3:
                    rel_height = max(0, height) / 0.3
                else:
                    rel_height = (height - 0.3) / 0.7
                    
                tiles[y % chunk_size[1]][x % chunk_size[0]] = tile_type(pygame.Vector2(x * self.tile_size, y * self.tile_size), self.tile_size, rel_height)

        return tiles

    @staticmethod
    def get_moore_neighborhood(array, coord: pygame.Vector2) -> list:
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
    def get_vnn_neighborhood(array, coord: pygame.Vector2 | tuple[int, int]) -> list:
        if len(array) == 0 or len(array[0]) == 0:
            return []

        return_arr = []
        if coord[0] > 0:
            return_arr.append((int(coord[0] - 1), int(coord[1])))
        if coord[0] < len(array) - 1:
            return_arr.append((int(coord[0]) + 1, int(coord[1])))
        if coord[1] > 0:
            return_arr.append((int(coord[0]), int(coord[1] - 1)))
        if coord[1] < len(array[0]) - 1:
            return_arr.append((int(coord[0]), int(coord[1] + 1)))

        return return_arr

    @timefunc
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
                    neighbors = World.get_vnn_neighborhood(height_map, pygame.Vector2(row_x, row_y))
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

    @timefunc
    @staticmethod
    def hydraulic_erosion(array) -> None:
        NotImplemented

    @timefunc
    @staticmethod
    def calculate_humidity_map_ff(heights, water_height=0.3):
        """Given a height map, create a map where each entry is the distance
        from the nearest water source. Returns an array with the same
        dimensions as `heights`
        """

        assert len(heights) > 0 and len(heights[0]) > 0

        size_x = len(heights)
        size_y = len(heights[0])

        output = [[None for _ in range(size_x)] for _ in range(size_y)]
        unseen = set(list((x, y) for x in range(size_x) for y in range(size_y)))
        
        # Step 1: Add all water as edge tiles
        edges = set()
        for x in range(size_x):
            for y in range(size_y):
                # Just look at water first
                if heights[x][y] < water_height:
                    output[x][y] = 0

                    unseen.remove((x, y))
                    edges.add((x, y))

        # Use flood fill to expand from the edge of water one tile at a time
        distance = 1
        while len(unseen) > 0:
            old_edges = list(edges)
            # Empty edges, because we want to look at each 'ring' of distances one at a time
            edges = set()
            for edge in old_edges:
                for coord in World.get_vnn_neighborhood(heights, edge):
                    if coord in unseen:
                        edges.add(coord)
                        unseen.remove(coord)
                        output[coord[0]][coord[1]] = distance
            distance += 1

        return output

    @timefunc
    def render_chunks(self) -> None:
        """Instead of rendering every tile every frame, we can render the tiles to chunks, and then draw whole
        chunks at a time. If a tile needs to be updated only the chunk needs to be re-rendered.
        """
        for chunk_pos in self.chunks:
            self.chunks[chunk_pos].render()

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the whole world, by going through each chunk"""

        for chunk_pos in self.chunks:
            self.chunks[chunk_pos].draw(surface, self.camera)
