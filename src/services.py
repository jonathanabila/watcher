import os
import sched
import socket
import time

import cpuinfo
import netifaces
import psutil
from texttable import Texttable

from helpers import clean_terminal, prettify, scheduler_timer


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


class DataUsageService:
    def __init__(self):
        self.network_service = NetworkService()

        self.interface_name = self.network_service.interface_name
        self._net = psutil.net_io_counters(pernic=True).get(self.interface_name)

        self.process_service = ProcessService()

    def __getattr__(self, item):
        return getattr(self, item, 0)

    @staticmethod
    def get_type(v):
        if v == socket.SOCK_STREAM:
            return "TPC"
        elif v == socket.SOCK_DGRAM:
            return "UPD"
        elif v == socket.SOCK_RAW:
            return "IP"
        else:
            return "-"

    @staticmethod
    def get_family(v):
        if v == socket.AF_INET:
            return "IPv4"
        elif v == socket.AF_INET6:
            return "IPv6"
        elif v == socket.AF_UNIX:
            return "Unix"
        else:
            return "-"

    @staticmethod
    def get_address(v):
        if hasattr(v, "ip"):
            return v.ip
        return None

    @staticmethod
    def get_port(v):
        if hasattr(v, "port"):
            return v.port
        return None

    @property
    def bytes_sent(self):
        return prettify(self._net.bytes_sent)

    @property
    def bytes_recv(self):
        return prettify(self._net.bytes_recv)

    @property
    def packets_recv(self):
        return self._net.packets_recv

    @property
    def packets_sent(self):
        return self._net.packets_sent

    @property
    def dropin(self):
        return self._net.dropin

    @property
    def dropout(self):
        return self._net.dropout

    @property
    def errin(self):
        return self._net.errin

    @property
    def errout(self):
        return self._net.errout

    def get_pids_connections(self):
        header = [
            "pid",
            "type",
            "family",
            "status",
            "local address",
            "local port",
            "remote address",
            "remote port",
        ]
        pid_connections = []

        pids = self.process_service.get_pids()
        for pid in pids:
            try:
                conns = psutil.Process(pid.pid).connections()
            except (psutil.AccessDenied, psutil.NoSuchProcess):
                continue

            for conn in conns:
                pid_connections.append(
                    [
                        pid.pid,
                        conn.type,
                        self.get_family(conn.family),
                        self.get_type(conn.status),
                        self.get_address(conn.laddr),
                        self.get_port(conn.laddr),
                        self.get_address(conn.raddr),
                        self.get_port(conn.raddr),
                    ]
                )

        return [header] + pid_connections


class NetworkService:
    def __init__(self):
        self.info = psutil.net_if_addrs()
        self.gateways = netifaces.gateways()

    @property
    def interface_name(self):
        return list(self.info.keys())[1]

    @property
    def _interface(self):
        return self.info.get(self.interface_name)[0]

    @property
    def ip(self):
        return self._interface.address

    @property
    def gateway(self):
        return list(self.gateways.get("default").values())[0][0]

    @property
    def sub_mask(self):
        return self._interface.netmask


class MemoryService:
    def __init__(self):
        self.info = psutil.virtual_memory()

    @property
    def total(self):
        return prettify(self.info.total)

    @property
    def available(self):
        return prettify(self.info.available)

    @property
    def usage(self):
        return (self.total - self.available) / self.total

    @property
    def pretty_usage(self):
        return round(self.usage, 2) * 100


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

    def get_pids(self):
        pids = []
        for pid in self.info:
            try:
                p = psutil.Process(pid)
                pids.append(p)
            except psutil.NoSuchProcess:
                continue
        return pids

    def pids(self):
        header = ["pid", "threads", "name", "memory", "cpu"]

        raw_pids = self.get_pids()

        pids = []
        for p in raw_pids:
            pids.append(
                [
                    p.pid,
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
        if len(sentences) > 1:
            t = Texttable()
            t.add_rows(sentences[:10])
            clean_terminal()
            print(t.draw())
