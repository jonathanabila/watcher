from dataclasses import dataclass
from typing import List


@dataclass
class CPUModel:
    usage_per_cpu: List[str]
    brand: str
    arch: str
    bits: str
    count: str
    logical_count: str
    max_frequency: str
    current_frequency: str


@dataclass
class MemoryModel:
    usage: str
    total: str
    available: str
    pretty_usage: str


@dataclass
class DiskModel:
    usage: str
    total: str
    available: str
    pretty_usage: str


@dataclass
class NetworkModel:
    ip: str
    interface_name: str
    gateway: str
    sub_mask: str


@dataclass
class ScannerModel:
    map_network: List
