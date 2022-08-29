import pygame

class Tile:

    def __init__(self, coord, size):
        self.position = coord
        self.size = self.width, self.height = size
        self.color = (255,255,255)

    def draw(self, surface):
        pygame.draw.rect(surface, self.color, (self.position.x, self.position.y, self.width, self.height), 2)