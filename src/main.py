from abc import ABC, abstractmethod

import pygame

from helpers import handle_quit

# Window
HEIGHT = 600
WIDTH = 800

# Font Configuration
FONT_SIZE = 20
FONT_STYLE = "freesansbold.ttf"

# Game Speed
FPS = 144
HITS_TO_INCREASE_SPEED = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Watcher")


class BaseComponent(ABC):
    @abstractmethod
    def draw(self, *args, **kwargs):
        pass


class Watcher(BaseComponent):
    def __init__(self):
        # Settings
        self.speed = FPS

    def draw(self, *args, **kwargs):
        pass


def main():
    pygame.init()
    clock = pygame.time.Clock()
    game = Watcher()

    while True:
        event = pygame.event.poll()
        if handle_quit(event):
            break

        screen.fill(BLACK)
        game.draw()
        pygame.display.update()
        clock.tick(game.speed)

    pygame.display.quit()
    pygame.quit()


if __name__ == "__main__":
    main()
