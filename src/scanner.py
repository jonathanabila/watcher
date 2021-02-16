import multiprocessing
import os
import subprocess

import nmap

POOL_SIZE = 255
INTERVAL_UPDATE = 100 * 20
DEVNULL = open(os.devnull, "w")


class Scanner:
    def __init__(self):
        self.nm = nmap.PortScanner()
        self.counter = 0

    @staticmethod
    def get_base_ip(raw_host):
        return ".".join(raw_host.split(".")[0:3]) + "."

    @staticmethod
    def _build_ping():
        """
        @https://phoenixnap.com/kb/linux-ping-command-examples
            c: Limits the number of sent ping requests.
            w: Specifies a time limit before the ping command exits, regardless
             of how many packets have been sent or received.
            W: Determines the time, in seconds, to wait for a response.
            l: Defines the number of packets to send without waiting for a reply
            n: Displays IP addresses in the ping output rather than hostnames.
        """
        if "nt" in os.name:
            return ["ping", "-n", "1", "-l", "1", "-w", "100"]
        else:
            return ["ping", "-c", "1", "-W", "1"]

    def _pinger(self, job_queue, results_queue):
        pinger_command = self._build_ping()
        while True:
            ip = job_queue.get()
            if ip is None:
                break
            try:
                subprocess.check_call([*pinger_command, ip], stdout=DEVNULL)
                results_queue.put(ip)
            except Exception:  # noqa: E722
                pass

    def _map_network(self, raw_host, pool_size):
        base_ip = self.get_base_ip(raw_host)
        ip_list = list()

        jobs = multiprocessing.Queue()
        results = multiprocessing.Queue()

        pool = [
            multiprocessing.Process(target=self._pinger, args=(jobs, results))
            for _ in range(pool_size)
        ]

        for p in pool:
            p.start()

        for i in range(1, 255):
            jobs.put(base_ip + "{0}".format(i))

        for _ in pool:
            jobs.put(None)

        for p in pool:
            p.join()

        while not results.empty():
            ip = results.get()
            ip_list.append(ip)

        return ip_list

    def map_network(self, raw_host, pool_size=POOL_SIZE):
        ip_list = list()
        if self.counter == 0:
            pass
        elif self.counter % INTERVAL_UPDATE == 0 or self.counter == 1:
            ip_list = self._map_network(raw_host, pool_size)

        self.counter += 1
        return ip_list
