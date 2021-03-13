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
    usage: str
