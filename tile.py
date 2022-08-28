import pygame

class Tile:

    def __init__(self, coord: pygame.Vector2, size: tuple[int, int]):
        self.position = coord
        self.size = self.width, self.height = size

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (255, 255, 255), (self.position.x, self.position.y, self.width, self.height), 2)