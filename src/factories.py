from abc import ABC, abstractmethod

from constants import Screens
from models import CPUModel, DiskModel, MemoryModel, NetworkModel, ScannerModel
from scanner import Scanner
from services import CPUService, DiskService, MemoryService, NetworkService


class BaseServiceStrategy(ABC):
    @property
    @abstractmethod
    def service(self):
        pass

    @property
    @abstractmethod
    def model(self):
        pass

    def execute(self):
        result = {}
        service = self.service()

        for i in list(self.model.__annotations__.keys()):
            result[i] = getattr(service, i)

        return self.model(**result)


class MethodServiceStrategy(BaseServiceStrategy, ABC):
    def execute(self):
        result = {}
        service = self.service

        for i in list(self.model.__annotations__.keys()):
            result[i] = getattr(service, i)(self.args)

        return self.model(**result)


class CPUStrategy(BaseServiceStrategy):
    service = CPUService
    model = CPUModel


class MemoryStrategy(BaseServiceStrategy):
    service = MemoryService
    model = MemoryModel


class DiskStrategy(BaseServiceStrategy):
    service = DiskService
    model = DiskModel


class NetworkStrategy(BaseServiceStrategy):
    service = NetworkService
    model = NetworkModel


class ScannerStrategy(MethodServiceStrategy):
    service = Scanner()
    model = ScannerModel

    def __init__(self, base_host):
        self.args = base_host[0]


class CommandsFactory:
    @staticmethod
    def build(commands):
        for command, args in commands:
            if command == Screens.CPU:
                yield CPUStrategy()
            if command == Screens.MEMORY:
                yield MemoryStrategy()
            if command == Screens.DISK:
                yield DiskStrategy()
            if command == Screens.NETWORK:
                yield NetworkStrategy()
            if command == Screens.SCANNER:
                yield ScannerStrategy(args)
