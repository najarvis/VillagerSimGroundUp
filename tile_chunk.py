from math import ceil
import pygame
from camera import Camera

from globals import DRAW_CHUNK_OUTLINES, SCREEN_SIZE, TILE_SIZE, CHUNK_SIZE

# Turns out "Chunk" is a python built-in
class TileChunk:
    """Segments tiles into a smaller sub-grid to save on memory and 
    drawing speed.
    
    Currently only stores the surface the tiles draw onto, but may (and 
    probably should) be modified to hold the tiles themselves.
    """

    SCREEN_RECT = pygame.Rect((0, 0, *SCREEN_SIZE))

    def __init__(self, coordinate: pygame.Vector2):
        self.coordinate = coordinate # These are in tile coordinates, not pixel coordinates
        self.width_px  = CHUNK_SIZE[0] * TILE_SIZE[0]
        self.height_px = CHUNK_SIZE[1] * TILE_SIZE[1]
        self.surface = pygame.Surface((self.width_px, self.height_px))
        self.scaled_surface = None
        self._last_scale = None

    def draw_to_chunk(self, surface, coordinate) -> None:
        self.surface.blit(surface, coordinate)

    def get_chunk_surf(self) -> pygame.Surface:
        return self.surface

    def draw(self, surface, camera: Camera) -> None:
        # TODO: Using ceil here to avoid annoying lines, but is causing some warping
        # Note: It does not seem to always remove the lines. Will need to revisit

        adjusted_coord = camera.world_to_screen(self.coordinate)

        bounds_rect = self.surface.get_rect()
        bounds_rect.w *= camera.scale
        bounds_rect.h *= camera.scale
        bounds_rect.topleft = adjusted_coord
        if not bounds_rect.colliderect(TileChunk.SCREEN_RECT):
            # Don't do the work of scaling an image if it won't be on the screen
            return

        if camera.scale != self._last_scale:
            # Don't scale an image if the camera hasn't changed scales
            self.scaled_surface = pygame.transform.scale(self.surface, (ceil(self.width_px  * camera.scale),
                                                                        ceil(self.height_px * camera.scale)))
            self._last_scale = camera.scale


        surface.blit(self.scaled_surface, adjusted_coord)

        if DRAW_CHUNK_OUTLINES:
            pygame.draw.rect(surface, (255, 0, 0), (adjusted_coord.x,
                                                    adjusted_coord.y,
                                                    self.width_px * camera.scale,
                                                    self.height_px * camera.scale), 1)