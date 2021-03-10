from abc import ABC, abstractmethod

from constants import Screens
from models import CPUModel
from services import CPUService


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


class CPUStrategy(BaseServiceStrategy):
    service = CPUService
    model = CPUModel


class CommandsFactory:
    @staticmethod
    def build(commands):
        for command, args in commands:
            if command == Screens.CPU:
                yield CPUStrategy()