from math import ceil
import pygame
from camera import Camera

from globals import DRAW_CHUNK_OUTLINES, TILE_SIZE, CHUNK_SIZE

# Turns out "Chunk" is a python built-in
class TileChunk:
    """Segments tiles into a smaller sub-grid to save on memory and 
    drawing speed.
    
    Currently only stores the surface the tiles draw onto, but may (and 
    probably should) be modified to hold the tiles themselves.
    """

    def __init__(self, coordinate: pygame.Vector2):
        self.coordinate = coordinate # These are in tile coordinates, not pixel coordinates
        self.width_px  = CHUNK_SIZE[0] * TILE_SIZE[0]
        self.height_px = CHUNK_SIZE[1] * TILE_SIZE[1]
        self.surface = pygame.Surface((self.width_px, self.height_px))

    def draw_to_chunk(self, surface, coordinate) -> None:
        self.surface.blit(surface, coordinate)

    def get_chunk_surf(self) -> pygame.Surface:
        return self.surface

    def draw(self, surface, camera: Camera) -> None:
        # TODO: Using ceil here to avoid annoying lines, but is causing some warping
        scaled_surf = pygame.transform.scale(self.surface, (ceil(self.width_px  * camera.scale),
                                                            ceil(self.height_px * camera.scale)))

        vec_to_camera = (self.coordinate - camera.position) * camera.scale
        adjusted_coord = pygame.Vector2(vec_to_camera.x * TILE_SIZE[0], vec_to_camera.y * TILE_SIZE[1])

        surface.blit(scaled_surf, adjusted_coord)

        # if DRAW_CHUNK_OUTLINES:
        #     pygame.draw.rect(surface, (255, 0, 0), (self.coordinate.x * self.width_px,
        #                                             self.coordinate.y * self.height_px,
        #                                             self.width_px, self.height_px), 1)