import pygame

SCREEN_SIZE = WIDTH, HEIGHT = (640, 480)

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