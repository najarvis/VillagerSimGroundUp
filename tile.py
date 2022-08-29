import pygame

class Tile:

    def __init__(self, coord: pygame.Vector2, size: int | tuple[int, int]):
        self.position = coord
        
        if type(size) is int:
            self.size = self.width, self.height = (size, size)
        else:
            self.size = self.width, self.height = size

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, (255, 255, 255), (self.position.x, self.position.y, self.width, self.height), 2)