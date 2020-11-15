import cpuinfo
import psutil


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
        return psutil.cpu_percent(percpu=True)


class NetworkService:
    def __init__(self):
        self.info = psutil.net_if_addrs()

    @property
    def ip(self):
        # TODO: make network interface dynamic
        return self.info["enp34s0"][0].address
