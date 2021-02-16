import os
import sched
import time

import cpuinfo
import psutil
from texttable import Texttable

from helpers import scheduler_timer


class Publisher:
    def __init__(self):
        self.subscribers = set()

    def register(self, who):
        self.subscribers.add(who)

    def unregister(self, who):
        self.subscribers.discard(who)

    def dispatch(self, event):
        for subscriber in self.subscribers:
            subscriber(event)


class CPUService:
    def __init__(self):
        self.info = cpuinfo.get_cpu_info()

    @property
    def brand(self):
        return self.info.get("brand_raw")

    @property
    def arch(self):
        return self.info.get("arch")

    @property
    def bits(self):
        return self.info.get("bits")

    @property
    def count(self):
        return psutil.cpu_count()

    @property
    def logical_count(self):
        return psutil.cpu_count(logical=True)

    @property
    def max_frequency(self):
        return psutil.cpu_freq().max

    @property
    def current_frequency(self):
        return round(psutil.cpu_freq().current, 1)

    @property
    def frequency_per_cpu(self):
        return psutil.cpu_freq(percpu=True)

    @property
    def usage(self):
        return psutil.cpu_percent()

    @property
    def usage_per_cpu(self):
        return [round(i / 100, 2) for i in psutil.cpu_percent(percpu=True)]


class NetworkService:
    def __init__(self):
        self.info = psutil.net_if_addrs()

    @property
    def ip(self):
        return self.info.get("enp34s0", list(self.info.keys())[0])[0].address


class MemoryService:
    def __init__(self):
        self.info = psutil.virtual_memory

    @staticmethod
    def _prettify(value):
        return round(value / (1024 * 1024 * 1024), 2)

    def total(self, pretty=False):
        return self.info().total if not pretty else self._prettify(self.info().total)

    def available(self, pretty=False):
        return (
            self.info().available
            if not pretty
            else self._prettify(self.info().available)
        )

    def usage(self, pretty=False):
        percentage = (self.total() - self.available()) / self.total()
        return percentage if not pretty else round(percentage, 2) * 100


class DiskService:
    def __init__(self):
        self.info = psutil.disk_usage(".")

    @staticmethod
    def _prettify(value):
        return round(value / (1024 * 1024 * 1024), 2)

    def total(self, pretty=False):
        return self.info.total if not pretty else self._prettify(self.info.total)

    def available(self, pretty=False):
        return self.info.free if not pretty else self._prettify(self.info.free)

    def usage(self, pretty=False):
        percentage = self.info.percent / 100
        return percentage if not pretty else round(percentage * 100, 2)


class ProcessService:
    def __init__(self):
        self.info = psutil.pids()

    def pids(self):
        header = ["pid", "threads", "name", "memory", "cpu"]

        pids = []
        for pid in self.info:
            try:
                p = psutil.Process(pid)
            except psutil.NoSuchProcess:
                continue

            pids.append(
                [
                    pid,
                    p.num_threads(),
                    p.name(),
                    round(p.memory_percent(), 1),
                    p.cpu_percent(),
                ]
            )

        return [header] + pids


class SystemService:
    def __init__(self):
        self.s = sched.scheduler(time.time, time.sleep)
        self.dirs_folder = []

    def _dirs(self):
        header = ["name", "type"]
        files = [
            [f, "folder" if os.path.isdir(f"../{f}") else "file"]
            for f in os.listdir("..")
        ]
        self.dirs_folder = [header] + files

    @scheduler_timer
    def _sched(self):
        self.s.enter(5, 1, self._dirs)
        # time.sleep(10)
        self.s.run()

    def dirs(self):
        if not self.dirs_folder:
            self._dirs()
            return self.dirs_folder

        self._sched()
        return self.dirs_folder


class TableService:
    @staticmethod
    def draw(sentences):
        t = Texttable()
        t.add_rows(sentences[:10])
        os.system("cls") if "nt" in os.name else os.system("clear")
        print(t.draw())
