import pygame

class Camera:

    def __init__(self, pos):
        self._scale = 1.0
        self.position = pos

    def world_to_screen(self, coord):
        return coord - self._scale * self.position

    def get_scale(self) -> float:
        return self._scale

    def set_scale(self, val) -> None:
        self._scale = max(0.1, min(val, 10))

    scale = property(get_scale, set_scale)