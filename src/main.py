from abc import ABC, abstractmethod

import pygame

from helpers import handle_quit
from services import CPUService, Publisher

# Window
HEIGHT = 600
WIDTH = 800

MARGIN_Y = 5
MARGIN_X = 35

# Font Configuration
FONT_SIZE = 13
FONT_STYLE = "freesansbold.ttf"

# Game Speed
FPS = 30
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


class Text(BaseComponent):
    def __init__(self):
        self.font = pygame.font.Font(FONT_STYLE, FONT_SIZE)

    def draw(self, title, position, *args, **kwargs):
        text = self.font.render(title, True, WHITE)
        screen.blit(text, position)
        return text.get_rect()


class BaseScreen(BaseComponent, ABC):
    def __init__(self):
        self.font = pygame.font.Font(FONT_STYLE, FONT_SIZE)

        self.spacing = 20
        self.start_position = 35

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

    def draw_details(self, details=None, *args, **kwargs):
        for idx, detail in enumerate(details):
            title, value, unit = detail

            position = MARGIN_X, MARGIN_Y + self.start_position + idx * self.spacing

            unit = "" if not unit else unit
            Text().draw(f"{title.title()}: {value} {unit}", position)

    def draw(self, *args, **kwargs):
        self._draw_text()


class CPUDetails(BaseScreen):
    title = "CPU"

    def __init__(self, cpu_service=None):
        self.cpu_service = cpu_service or CPUService()
        super().__init__()

    def draw_details(self, details=None, *args, **kwargs):
        details = [
            ("name", self.cpu_service.brand, None),
            ("architecture", self.cpu_service.arch, None),
            ("bits", self.cpu_service.bits, None),
            ("cores", self.cpu_service.count, None),
            ("logical cores", self.cpu_service.logical_count, None),
            ("max frequency", self.cpu_service.max_frequency, "Hz"),
            ("frequency", self.cpu_service.current_frequency, "Hz"),
        ]
        super(CPUDetails, self).draw_details(details)

    def draw(self, *args, **kwargs):
        self.draw_details()
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
        self.is_summary_open = False

        self.screen_idx = None

    def draw(self, *args, **kwargs):
        if not self.screen_idx:
            self.screen_idx = 0

        if self.is_summary_open:
            self.summary[0].draw()
        else:
            self.screens[self.screen_idx].draw()

    def _handle_summary(self):
        if self.is_summary_open:
            self.is_summary_open = False
        else:
            self.is_summary_open = True

    def _move_carousel(self, direction):
        self.is_summary_open = False
        screens_pos = len(self.screens) - 1
        if self.screen_idx == 0 and direction < 0:
            self.screen_idx = screens_pos
        elif self.screen_idx == screens_pos and direction > 0:
            self.screen_idx = 0
        else:
            self.screen_idx += direction

    def handle_event(self, event):
        if event.key == pygame.K_SPACE:
            self._handle_summary()
        elif event.key == pygame.K_LEFT:
            self._move_carousel(-1)
        elif event.key == pygame.K_RIGHT:
            self._move_carousel(1)


def main():
    pygame.init()
    clock = pygame.time.Clock()
    watcher = Watcher()

    pub = Publisher()
    pub.register(watcher.handle_event)

    while True:
        event = pygame.event.poll()
        if handle_quit(event):
            break

        if event.type == pygame.KEYDOWN:
            pub.dispatch(event)

        screen.fill(BLACK)
        watcher.draw()
        pygame.display.update()
        clock.tick(watcher.speed)

    pygame.display.quit()
    pygame.quit()


if __name__ == "__main__":
    main()
