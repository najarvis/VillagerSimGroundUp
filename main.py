import pygame

SCREEN_SIZE = WIDTH, HEIGHT = (640, 480)

WORLD_SIZE = (20, 20)
TILE_SIZE = (32, 32)

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


        pygame.display.update()

if __name__ == "__main__":
    run()