import random
import pygame

class Tile:

    noise_texture = pygame.Surface((16, 16))
    for x in range(16):
        for y in range(16):
            c = random.randint(225, 255)
            col = (c, c, c)
            noise_texture.set_at((x, y), col)

    light_tex = pygame.Surface((16, 16))
    light_tex.fill((30, 30, 30))
    
    def __init__(self, coord: pygame.Vector2, size: int | tuple[int, int], height: float=1.0):
        self.position = coord
        
        if type(size) is int:
            self.size = self.width, self.height = (size, size)
        else:
            self.size = self.width, self.height = size
            
        self.color = (255, 0, 0) # Red for debug purposes
        self.shadow = pygame.Surface(self.size)
        self.shadow.set_alpha(min(255, (1.0 - height) * 127))
        self.use_noise = True

    def draw(self, surface, position_override: pygame.Vector2 | None = None) -> None:
        draw_pos = self.position
        if position_override is not None:
            draw_pos = position_override

        pygame.draw.rect(surface, self.color, (draw_pos.x, draw_pos.y, self.width, self.height))
        if self.use_noise:
            surface.blit(Tile.noise_texture, draw_pos, special_flags=pygame.BLEND_MULT)
            surface.blit(Tile.light_tex, draw_pos, special_flags=pygame.BLEND_ADD)
        surface.blit(self.shadow, draw_pos)