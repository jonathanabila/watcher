from abc import ABC, abstractmethod

import main
from client import get_details
from constants import Screens


class BaseSocketScreen(main.BaseScreen, ABC):
    @property
    @abstractmethod
    def screen_command(self):
        return

    @abstractmethod
    def get_details(self):
        pass

    def draw(self, *args, **kwargs):
        self.get_details()
        super().draw(*args, **kwargs)


class SocketCPUDetails(BaseSocketScreen, main.CPUDetails):
    screen_command = Screens.CPU

    def __init__(self):
        super().__init__(cpu_service=get_details(self.screen_command))

    def get_details(self):
        self.cpu_service = get_details(self.screen_command)


class SocketMemoryDetails(BaseSocketScreen, main.MemoryDetails):
    screen_command = Screens.MEMORY

    def __init__(self):
        super().__init__(memory_service=get_details(self.screen_command))

    def get_details(self):
        self.memory_service = get_details(self.screen_command)


class SocketDiskDetails(BaseSocketScreen, main.DiskDetails):
    screen_command = Screens.DISK

    def __init__(self):
        super().__init__(disk_service=get_details(self.screen_command))

    def get_details(self):
        self.disk_service = get_details(self.screen_command)


class SocketWatcher(main.Watcher):
    def __init__(self, screens=None, summary=None):
        screens = (
            SocketCPUDetails(),
            SocketMemoryDetails(),
            SocketDiskDetails(),
        )

        super().__init__(screens, summary)


if __name__ == "__main__":
    main.main(lambda: SocketWatcher())
