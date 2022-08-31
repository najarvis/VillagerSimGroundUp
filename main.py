import pygame

from globals import SCREEN_SIZE
from world import World

def run():
    screen = pygame.display.set_mode(SCREEN_SIZE)

    # Main world instance 
    world = World()
    
    clock = pygame.time.Clock()

    done = False
    while not done:
        delta = clock.tick() / 1000.0 # time passed in seconds since last call
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
                    
                if event.key == pygame.K_F2:
                    pygame.image.save(screen, "SCREENSHOT.png")
                    
        screen.fill((0, 0, 0))
        
        # Draw the screen
        world.draw(screen)
        
        pygame.display.update()
        pygame.display.set_caption(f"FPS: {round(clock.get_fps(), 2)}")

if __name__ == "__main__":
    run()