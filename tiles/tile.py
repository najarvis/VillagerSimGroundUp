import pygame

class Tile:
    
    def __init__(self, coord: pygame.Vector2, size: int | tuple[int, int]):
        self.position = coord
        
        if type(size) is int:
            self.size = self.width, self.height = (size, size)
        else:
            self.size = self.width, self.height = size
            
        self.color = (255, 255, 255)

    def draw(self, surface, position_override: pygame.Vector2 | None = None) -> None:
        draw_pos = self.position
        if position_override is not None:
            draw_pos = position_override

        pygame.draw.rect(surface, self.color, (draw_pos.x, draw_pos.y, self.width, self.height))