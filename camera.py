import pygame

class Camera:
    """Used to keep track of what should be on the screen. 
    Represents the virtual camera.
    """

    def __init__(self, pos: pygame.Vector2):
        self._scale = 1.0
        self.position = pos

    def world_to_screen(self, coord):
        # something like (coord - self.position) * self._scale
        NotImplemented

    def get_scale(self) -> float:
        return self._scale

    def set_scale(self, val) -> None:
        # clamp the values
        self._scale = max(0.1, min(val, 10))

    scale = property(get_scale, set_scale)