import pygame

from globals import TILE_SIZE, CHUNK_SIZE

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

    def draw(self, surface) -> None:
        surface.blit(self.surface, (self.coordinate.x * self.width_px,
                                    self.coordinate.y * self.height_px))