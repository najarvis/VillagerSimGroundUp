import pygame

from globals import *

from tile import Tile
from world import World

def run():
    screen = pygame.display.set_mode(SCREEN_SIZE)

    # Main game 
    world = World(WORLD_SIZE)

    done = False
    while not done:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
                    
        screen.fill((0, 0, 0))
        
        # Draw the screen
        world.draw(screen)
        
        pygame.display.update()

if __name__ == "__main__":
    run()