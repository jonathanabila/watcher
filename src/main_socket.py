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


class SocketNetworkDetails(BaseSocketScreen, main.NetworkDetails):
    screen_command = Screens.NETWORK

    def __init__(self):
        super().__init__(
            network_service=get_details(self.screen_command),
            scanner_service=get_details(Screens.SCANNER, None),
        )

    def get_map_network(self, internal_ip):
        return get_details(Screens.SCANNER, internal_ip).map_network

    def get_details(self):
        self.network_service = get_details(self.screen_command)


class SocketProcessDetails(BaseSocketScreen, main.ProcessDetails):
    screen_command = Screens.PROCESS

    def __init__(self):
        super().__init__(process_service=get_details(self.screen_command))

    def get_details(self):
        self.process_service = get_details(self.screen_command)


class SocketDataUsageDetails(BaseSocketScreen, main.DataUsageDetails):
    screen_command = Screens.DATA_USAGE

    def __init__(self):
        super().__init__(data_usage_service=get_details(self.screen_command))

    def get_details(self):
        self.dt_service = get_details(self.screen_command)


class SocketSystemDetails(BaseSocketScreen, main.SystemDetails):
    screen_command = Screens.SYSTEM

    def __init__(self):
        super().__init__(system_service=get_details(self.screen_command))

    def get_details(self):
        self.system_service = get_details(self.screen_command)


class SocketSummary(main.Summary):
    screen_command = Screens.SUMMARY

    def __init__(self):
        super().__init__(
            disk_details=SocketDiskDetails(),
            cpu_details=SocketCPUDetails(),
            memory_details=SocketMemoryDetails(),
        )

    def draw(self, *args, **kwargs):
        self.disk_details = SocketDiskDetails()
        self.cpu_details = SocketCPUDetails()
        self.memory_details = SocketMemoryDetails()

        super().draw()


class SocketWatcher(main.Watcher):
    def __init__(self, screens=None, summary=None):
        screens = (
            SocketCPUDetails(),
            SocketMemoryDetails(),
            SocketDiskDetails(),
            SocketNetworkDetails(),
            SocketProcessDetails(),
            SocketDataUsageDetails(),
            SocketSystemDetails(),
        )

        summary = (SocketSummary(),)

        super().__init__(screens, summary)


if __name__ == "__main__":
    main.main(lambda: SocketWatcher())
