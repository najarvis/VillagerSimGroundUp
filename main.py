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
        # Limit to 60 fps to avoid doing unnecessary work on the CPU
        delta = clock.tick(60) / 1000.0 # time passed in seconds since last call
        pos = pygame.Vector2(*pygame.mouse.get_pos())
        
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
                # Zoom relative to the mouse position steps: (credit: https://stackoverflow.com/a/21614272)
                # 1) Get the world-space coordinates of the mouse cursor using the current zoom factor and model/proj/view matrices.
                # 2) Adjust zoom factor
                # 3) Get the world-space mouse coordinates again using the new zoom factor
                # 4) Shift the camera position by the difference in world-space mouse coordinates
                # 5) Redraw scene using new camera position and zoom factor (already taken care of)

                # 1
                mouse_pos_world = world.camera.screen_to_world(pygame.Vector2(pos))

                # 2
                zoom_percentage = 0.10 # What percentage we zoom in with each notch of the mouse wheel
                world.camera.scale *= (event.y * zoom_percentage) + 1.0 #event.y is either 1 or -1 depending on direction

                # 3
                new_mouse_pos_world = world.camera.screen_to_world(pygame.Vector2(pos))

                # 4
                world.camera.position += mouse_pos_world - new_mouse_pos_world

        # Pan if the user has their mouse on the outside of the screen
        if pygame.mouse.get_focused():
            if pos.x < SCREEN_SIZE[0] * 0.10:
                world.camera.position.x -= 1 / world.camera.scale

            elif pos.x > SCREEN_SIZE[0] * 0.90:
                world.camera.position.x += 1 / world.camera.scale

            if pos.y < SCREEN_SIZE[1] * 0.10:
                world.camera.position.y -= 1 / world.camera.scale

            elif pos.y > SCREEN_SIZE[1] * 0.90:
                world.camera.position.y += 1 / world.camera.scale

        world.update(delta)

        screen.fill((0, 0, 0))
        
        # Draw the screen
        world.draw(screen)
        
        pygame.display.update()
        pygame.display.set_caption(f"FPS: {round(clock.get_fps(), 2)}")

if __name__ == "__main__":
    run()