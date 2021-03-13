from abc import ABC, abstractmethod

import pygame

from helpers import clean_terminal, handle_quit
from scanner import Scanner
from services import (
    CPUService,
    DataUsageService,
    DiskService,
    MemoryService,
    NetworkService,
    ProcessService,
    Publisher,
    SystemService,
    TableService,
)

SLEEP_INTERVAL = 0.5

# Window
HEIGHT = 600
WIDTH = 800

MARGIN_Y = 5
MARGIN_X = 35

# Font Configuration
FONT_SIZE = 13
FONT_STYLE = "freesansbold.ttf"

# Game Speed
FPS = 10
HITS_TO_INCREASE_SPEED = 10

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

EMPTY_LINES = (("", None, None),) * 2

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


class Rect(BaseComponent):
    def __init__(self, x, y, width, height):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self, color):
        pygame.draw.rect(screen, color, self.rect)


class UsageBar(BaseComponent):
    SPACING = 20

    def draw(self, percentage, y_start, width, height):
        x = MARGIN_X
        y_start += self.SPACING  # Spacing between components

        Rect(x, y_start, width, height).draw(BLUE)
        Rect(x, y_start, width * percentage, height).draw(RED)


class VerticalUsageBar(BaseComponent):
    def draw(self, percentage, position, width, height):
        x, y = position

        Rect(x, y, width, height).draw(BLUE)
        Rect(x, y + height - height * percentage, width, height * percentage).draw(RED)


class BaseScreen(BaseComponent, ABC):
    def __init__(self):
        self.font = pygame.font.Font(FONT_STYLE, FONT_SIZE)

        self.spacing = 20
        self.start_position = 35

        self.bar_height = 50

    @property
    def title(self):
        return self.title

    @staticmethod
    def _get_text_center():
        return MARGIN_X, MARGIN_Y

    def _draw_text(self):
        # TODO: use Text class
        text = self.font.render(self.title, True, WHITE)
        x, y = self._get_text_center()
        screen.blit(text, (x, y))

    def _draw_frame(self):
        pass

    @abstractmethod
    def draw_details(self, details=None, *args, **kwargs):
        for idx, detail in enumerate(details):
            title, value, unit = detail

            position = MARGIN_X, MARGIN_Y + self.start_position + idx * self.spacing

            unit = "" if not unit else unit
            line = (
                title.title() if value is None else f"{title.title()}: {value} {unit}"
            )
            Text().draw(line, position)

    @abstractmethod
    def draw_usage(self, usage=None, y_start=None, title=None):
        # Moves a little further from the details
        y_start += 40

        Text().draw(f"{self.title if not title else title} usage:", (MARGIN_X, y_start))

        width = WIDTH - 2 * MARGIN_X
        height = self.bar_height

        UsageBar().draw(usage, y_start, width, height)

    def draw(self, *args, **kwargs):
        self._draw_text()

        self.draw_details()
        self.draw_usage()


class CPUDetails(BaseScreen):
    title = "CPU"

    def __init__(self, cpu_service=None):
        self.cpu_service = cpu_service or CPUService()
        super().__init__()

    def draw_usage(self, usage=None, position=None, height=None):
        right_margin = 15  # margin between bars
        y = 200  # Start point on y

        usages = self.cpu_service.usage_per_cpu

        width = ((WIDTH - 2 * MARGIN_X) / len(usages)) - right_margin
        height = HEIGHT - 20 - y - MARGIN_Y

        for idx, usage in enumerate(usages):
            x = MARGIN_X + right_margin / 2 + idx * (right_margin + width)

            position = x, y
            VerticalUsageBar().draw(usage, position, width, height)

    def draw_details(self, details=None, *args, **kwargs):
        details = [
            ("name", self.cpu_service.brand, None),
            ("architecture", self.cpu_service.arch, None),
            ("bits", self.cpu_service.bits, None),
            ("cores", self.cpu_service.count, None),
            ("logical cores", self.cpu_service.logical_count, None),
            ("max frequency", self.cpu_service.max_frequency, "MHz"),
            ("frequency", self.cpu_service.current_frequency, "MHz"),
        ]
        super().draw_details(details)

    def draw(self, *args, **kwargs):
        super().draw(*args, **kwargs)


class MemoryDetails(BaseScreen):
    title = "Memory"

    def __init__(self, memory_service=None):
        self.memory_service = memory_service or MemoryService()
        super().__init__()

    def draw_usage(self, usage=None, position=None, height=None):
        usage = self.memory_service.usage

        y_start = 80 if not position else position
        super().draw_usage(usage, y_start)

    def draw_details(self, details=None, *args, **kwargs):
        details = [
            ("Total", self.memory_service.total, "Gb"),
            ("Available", self.memory_service.available, "Gb"),
            ("Usage", self.memory_service.pretty_usage, "%"),
        ]
        super().draw_details(details)

    def draw(self, *args, **kwargs):
        super().draw(*args, **kwargs)


class DiskDetails(BaseScreen):
    title = "Disk"

    def __init__(self, disk_service=None):
        self.disk_service = disk_service or DiskService()
        super().__init__()

    def draw_usage(self, usage=None, position=None, height=None):
        usage = self.disk_service.usage

        y_start = 80 if not position else position
        super().draw_usage(usage, y_start)

    def draw_details(self, details=None, *args, **kwargs):
        details = [
            ("Total", self.disk_service.total, "Gb"),
            ("Available", self.disk_service.available, "Gb"),
            ("Usage", self.disk_service.pretty_usage, "%"),
        ]
        super().draw_details(details)

    def draw(self, *args, **kwargs):
        super().draw(*args, **kwargs)


class DataUsageDetails(BaseScreen):
    title = "Data Usage"

    def __init__(self, data_usage_service=None, table_service=None):
        self.dt_service = data_usage_service or DataUsageService()
        self.table_service = table_service or TableService()
        super().__init__()

    def draw_usage(self, usage=None, y_start=None, title=None):
        pass

    def draw_details(self, details=None, *args, **kwargs):
        details = [
            ("Interface", self.dt_service.interface_name, None),
            ("Data sent", self.dt_service.bytes_sent, "Gb"),
            ("Data received", self.dt_service.bytes_recv, "Gb"),
            ("Packages sent", self.dt_service.packets_sent, None),
            ("Packages received", self.dt_service.packets_recv, None),
            ("Dropin", self.dt_service.dropin, None),
            ("Dropout", self.dt_service.dropout, None),
            ("Errin", self.dt_service.errin, None),
            ("Errout", self.dt_service.errout, None),
        ]
        super().draw_details(details)

        pids_connections = self.dt_service.pids_connections
        self.table_service.draw(pids_connections)


class NetworkDetails(BaseScreen):
    title = "Network"

    def __init__(self, network_service=None, scanner_service=None, table_service=None):
        self.network_service = network_service or NetworkService()
        self.scanner_service = scanner_service or Scanner()
        self.table_service = table_service or TableService()
        super().__init__()

    def draw_usage(self, usage=None, position=None, height=None):
        pass

    def get_map_network(self, internal_ip):
        return self.scanner_service.map_network(internal_ip)

    def draw_details(self, details=None, *args, **kwargs):
        internal_ip = self.network_service.ip
        details = [
            ("Interface", self.network_service.interface_name, None),
            ("IP", internal_ip, None),
            ("Gateway", self.network_service.gateway, None),
            ("SubMask", self.network_service.sub_mask, None),
            *EMPTY_LINES,
            ("More details on the terminal", "", None),
        ]
        super().draw_details(details)

        subnet_hosts = self.get_map_network(internal_ip)
        self.table_service.draw(subnet_hosts)

    def draw(self, *args, **kwargs):
        self.draw_details()
        super().draw(*args, **kwargs)


class ProcessDetails(BaseScreen):
    title = "Process"

    def __init__(self, process_service=None, table_service=None):
        self.process_service = process_service or ProcessService()
        self.table_service = table_service or TableService()
        super().__init__()

    def draw_details(self, details=None, *args, **kwargs):
        Text().draw("Output on the terminal.", (MARGIN_X, 40))
        pids = self.process_service.pids
        self.table_service.draw(pids)

    def draw_usage(self, usage=None, y_start=None, title=None):
        pass


class SystemDetails(BaseScreen):
    title = "System"

    def __init__(self, system_service=None, table_service=None):
        self.system_service = system_service or SystemService()
        self.table_service = table_service or TableService()
        super().__init__()

    def draw_details(self, details=None, *args, **kwargs):
        Text().draw("Output on the terminal.", (MARGIN_X, 40))
        dirs = self.system_service.dirs()
        self.table_service.draw(dirs)

    def draw_usage(self, usage=None, y_start=None, title=None):
        pass


class Summary(BaseScreen):
    title = "Summary"

    def __init__(self, disk_details=None, cpu_details=None, memory_details=None):
        self.disk_details = disk_details or DiskDetails()
        self.cpu_details = cpu_details or CPUDetails()
        self.memory_details = memory_details or MemoryDetails()
        super().__init__()

    def draw_usage(self, usage=None, position=None, height=None):
        self.cpu_details.draw_details()
        self.disk_details.draw_usage(position=150)
        self.memory_details.draw_usage(position=225)

    def draw_details(self, details=None, *args, **kwargs):
        pass

    def draw(self, *args, **kwargs):
        super().draw(*args, **kwargs)


class Watcher(BaseComponent):
    def __init__(self, screens=None, summary=None):
        # Settings
        self.speed = FPS

        self.screens = screens or (
            CPUDetails(),
            MemoryDetails(),
            DiskDetails(),
            NetworkDetails(),
            ProcessDetails(),
            DataUsageDetails(),
            SystemDetails(),
        )
        self.summary = summary or (Summary(),)
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

        clean_terminal()

    def handle_event(self, event):
        if event.key == pygame.K_SPACE:
            self._handle_summary()
        elif event.key == pygame.K_LEFT:
            self._move_carousel(-1)
        elif event.key == pygame.K_RIGHT:
            self._move_carousel(1)


def main(watcher=None):
    is_running = True

    pygame.init()
    clock = pygame.time.Clock()
    watcher = watcher() if callable(watcher) else Watcher()

    pub = Publisher()
    pub.register(watcher.handle_event)

    clean_terminal()

    while is_running:
        events = pygame.event.get()

        for event in events:
            if event.type == pygame.KEYDOWN:
                pub.dispatch(event)

            if handle_quit(event):
                is_running = False

        screen.fill(BLACK)
        watcher.draw()
        pygame.display.update()
        clock.tick(watcher.speed)

    pygame.display.quit()
    pygame.quit()


if __name__ == "__main__":
    main()
