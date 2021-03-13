from enum import Enum


class EnumChoices(Enum):
    def __str__(self):
        return self.value


class Screens(EnumChoices):
    CPU = "CPU"
    MEMORY = "MEMORY"
    DISK = "DISK"
    NETWORK = "NETWORK"
    SCANNER = "SCANNER"
    PROCESS = "PROCESS"
    DATA_USAGE = "DATA_USAGE"
    SYSTEM = "SYSTEM"

    SUMMARY = "SUMMARY"
