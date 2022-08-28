import pygame

class Tile:

    def __init__(self, coord, size):
        self.position = coord
        self.size = self.width, self.height = size

    def draw(self, surface):
        pygame.draw.rect(surface, (255, 255, 255), (self.position.x, self.position.y, self.width, self.height), 2)