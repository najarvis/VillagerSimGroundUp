import pygame

from tile import Tile

SCREEN_SIZE = WIDTH, HEIGHT = (640, 640)

WORLD_SIZE = (20, 20)
TILE_SIZE = (32, 32)

tiles = [[Tile(pygame.Vector2(x * TILE_SIZE[0], y * TILE_SIZE[1]), TILE_SIZE) for x in range(WORLD_SIZE[0])] for y in range(WORLD_SIZE[1])]

def run():
    screen = pygame.display.set_mode(SCREEN_SIZE)

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True

        for tile_row in tiles:
            for tile in tile_row:
                tile.draw(screen)
            
        pygame.display.update()

if __name__ == "__main__":
    run()