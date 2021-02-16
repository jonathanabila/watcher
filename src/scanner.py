import os
import subprocess

import nmap

from helpers import threader

POOL_SIZE = 255
INTERVAL_UPDATE = 100 * 20
PORTS = "22,80,443"

DEVNULL = open(os.devnull, "w")


class Scanner:
    def __init__(self):
        self.nm = nmap.PortScanner()
        self.counter = 0

        self.scanned = []

    @staticmethod
    def get_base_ip(raw_host):
        return ".".join(raw_host.split(".")[0:3])

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
        ips = [f"{base_ip}.{i}" for i in range(255)]

        return threader(self._pinger, ips, pool_size)

    def _map_network_ports(self, host):
        result = []

        self.nm.scan(host, ports=PORTS)
        try:
            for protocol in self.nm[host].all_protocols():
                for port in self.nm[host][protocol].keys():
                    state = self.nm[host][protocol][port]["state"]
                    result.append((port, state))
        except KeyError:
            pass

        return result

    def map_network(self, raw_host, pool_size=POOL_SIZE):
        header = ["host", "port", "state"]
        self.counter += 1

        if self.counter == 0 or self.counter < 10:
            return self.scanned
        elif self.counter % INTERVAL_UPDATE == 0 or self.counter == 10:
            hosts = self._map_network(raw_host, pool_size)
            for host in hosts:
                ports = self._map_network_ports(host)
                for port in ports:
                    self.scanned.append([host, port[0], port[1]])

        return [header] + self.scanned
