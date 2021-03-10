from abc import ABC, abstractmethod

import main
from client import get_details


class BaseSocketScreen(main.BaseScreen, ABC):
    @abstractmethod
    def get_details(self):
        pass

    def draw(self, *args, **kwargs):
        self.get_details()
        super().draw(*args, **kwargs)


class SocketCPUDetails(BaseSocketScreen, main.CPUDetails):
    def get_details(self):
        self.cpu_service = get_details()

    def __init__(self):
        super().__init__(cpu_service=get_details())


class SocketWatcher(main.Watcher):
    def __init__(self, screens=None, summary=None):
        screens = (SocketCPUDetails(),)

        super().__init__(screens, summary)


if __name__ == "__main__":
    main.main(lambda: SocketWatcher())
