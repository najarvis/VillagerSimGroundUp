import math
import pygame

from globals import SCREEN_SIZE
from world import World

def run():
    screen = pygame.display.set_mode(SCREEN_SIZE)

    # Main world instance 
    world = World()
    
    clock = pygame.time.Clock()

    t = 0

    done = False
    while not done:
        # Limit to 60 fps to avoid doing unnecessary work on the CPU
        delta = clock.tick(60) / 1000.0 # time passed in seconds since last call
        t += delta
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    done = True
                    
                if event.key == pygame.K_F2:
                    pygame.image.save(screen, "SCREENSHOT.png")

                if event.key == pygame.K_SPACE:
                    world.generate()
                    world.render_chunks()

            elif event.type == pygame.MOUSEWHEEL:
                world.camera.scale += event.y * 0.05

        if pygame.mouse.get_focused():
            pos = pygame.Vector2(*pygame.mouse.get_pos())
            if pos.x < SCREEN_SIZE[0] * 0.10:
                world.camera.position.x -= 1

            elif pos.x > SCREEN_SIZE[0] * 0.90:
                world.camera.position.x += 1

            if pos.y < SCREEN_SIZE[1] * 0.10:
                world.camera.position.y -= 1

            elif pos.y > SCREEN_SIZE[1] * 0.90:
                world.camera.position.y += 1 

        world.update(delta)

        screen.fill((0, 0, 0))
        
        # Draw the screen
        world.draw(screen)
        
        pygame.display.update()
        pygame.display.set_caption(f"FPS: {round(clock.get_fps(), 2)}")

if __name__ == "__main__":
    run()