import pygame

class Tile:
    
    def __init__(self, coord: pygame.Vector2, size: int | tuple[int, int]):
        self.position = coord
        
        if type(size) is int:
            self.size = self.width, self.height = (size, size)
        else:
            self.size = self.width, self.height = size
            
        self.color = (255, 255, 255)

    def draw(self, surface, position_override=None):
        pos = self.position
        if position_override is not None:
            pos = position_override
        pygame.draw.rect(surface, self.color, (pos.x, pos.y, self.width, self.height))