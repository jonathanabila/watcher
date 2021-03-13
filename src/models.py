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


@dataclass
class ProcessModel:
    pids: List


@dataclass
class DataUsageModel:
    interface_name: str
    bytes_sent: str
    bytes_recv: str
    packets_sent: str
    packets_recv: str
    dropin: str
    dropout: str
    errin: str
    errout: str
    pids_connections: List


@dataclass
class SystemModel:
    dirs: List
