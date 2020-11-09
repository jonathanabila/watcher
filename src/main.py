from abc import ABC, abstractmethod

import pygame

from helpers import handle_quit

# Window
HEIGHT = 600
WIDTH = 800

MARGIN_Y = 5
MARGIN_X = 35

# Font Configuration
FONT_SIZE = 13
FONT_STYLE = "freesansbold.ttf"

# Game Speed
FPS = 144
HITS_TO_INCREASE_SPEED = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Watcher")


class BaseComponent(ABC):
    @abstractmethod
    def draw(self, *args, **kwargs):
        pass


class BaseScreen(BaseComponent, ABC):
    def __init__(self):
        self.font = pygame.font.Font(FONT_STYLE, FONT_SIZE)

    @property
    def title(self):
        return self.title

    @staticmethod
    def _get_text_center():
        return MARGIN_X, MARGIN_Y

    def _draw_text(self):
        text = self.font.render(self.title, True, WHITE)
        x, y = self._get_text_center()
        screen.blit(text, (x, y))

    def _draw_frame(self):
        pass

    def draw(self, *args, **kwargs):
        self._draw_text()


class CPUDetails(BaseScreen):
    title = "CPU"

    def draw(self, *args, **kwargs):
        super().draw(*args, **kwargs)


class MemoryDetails(BaseScreen):
    title = "Memory"

    def draw(self, *args, **kwargs):
        super().draw(*args, **kwargs)


class DiskDetails(BaseScreen):
    title = "Disk"

    def draw(self, *args, **kwargs):
        super().draw(*args, **kwargs)


class NetworkDetails(BaseScreen):
    title = "Network"

    def draw(self, *args, **kwargs):
        super().draw(*args, **kwargs)


class Summary(BaseScreen):
    title = "Summary"

    def draw(self, *args, **kwargs):
        super().draw(*args, **kwargs)


class Watcher(BaseComponent):
    def __init__(self):
        # Settings
        self.speed = FPS

        self.screens = (
            CPUDetails(),
            MemoryDetails(),
            DiskDetails(),
            NetworkDetails(),
        )
        self.summary = (Summary(),)

        self.screen_idx = None

    def draw(self, *args, **kwargs):
        if not self.screen_idx:
            self.screen_idx = 0

        self.screens[self.screen_idx].draw()

    def _move_carousel(self, direction):
        screens_pos = len(self.screens) - 1
        if self.screen_idx == 0 and direction < 0:
            self.screen_idx = screens_pos
        elif self.screen_idx == screens_pos and direction > 0:
            self.screen_idx = 0
        else:
            self.screen_idx += direction

    def handle_event(self):
        key = pygame.key.get_pressed()
        if key[pygame.K_SPACE]:
            self.draw(self.summary)
        elif key[pygame.K_LEFT]:
            self._move_carousel(-1)
        elif key[pygame.K_RIGHT]:
            self._move_carousel(1)


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
        game.handle_event()
        pygame.display.update()
        clock.tick(game.speed)

    pygame.display.quit()
    pygame.quit()


if __name__ == "__main__":
    main()
