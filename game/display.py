import pygame


class DisplayMode:
    def __init__(self, surface):
        self.surface = surface
        self.window_size = surface.get_size()
        self.fullscreen = False

    def handle_event(self, event):
        if event.type == pygame.VIDEORESIZE and not self.fullscreen:
            self.window_size = (max(1, event.w), max(1, event.h))
            self.surface = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
        elif event.type == pygame.KEYDOWN and event.key == pygame.K_F11:
            self.toggle_fullscreen()
        return self.surface

    def toggle_fullscreen(self):
        if self.fullscreen:
            self.surface = pygame.display.set_mode(self.window_size, pygame.RESIZABLE)
            self.fullscreen = False
        else:
            self.window_size = self.surface.get_size()
            self.surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
            self.fullscreen = True
        return self.surface
