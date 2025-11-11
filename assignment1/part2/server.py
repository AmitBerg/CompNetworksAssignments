import socket
import time
import sys
from sys import argv
from typing import List

NO_DOMAIN_ENTRY_STR = "non-existent domain"

class DomainEntry:
    TYPE_NS = "NS"
    TYPE_A = "A"
    def __init__(self, domain: str, ip: str, entry_type: str, expire_time: float = None):
        self.domain = domain.strip()
        self.ip = ip.strip()
        self.entry_type = entry_type.strip()
        self.expire_time = expire_time

    def __str__(self):
        return f"{self.domain},{self.ip},{self.entry_type}"

    def is_expired(self) -> bool:
        if self.expire_time is None:
            return False
        return time.time() >= self.expire_time

class DomainList:
    def __init__(self):
        self.domains : List[DomainEntry] = []

    def add(self, entry: DomainEntry):
        self.domains.append(entry)

    def remove_expired(self):
        self.domains = [entry for entry in self.domains if not entry.is_expired()]

    def resolve(self, query: str) -> str:
        self.remove_expired()
        for domain_entry in self.domains:
            # print(f"Checking domain entry: {domain_entry} for query: {query}, entry_type: {domain_entry.entry_type}")
            # print(f"{domain_entry.domain == query}, {domain_entry.entry_type == DomainEntry.TYPE_A}")
            if domain_entry.domain == query and domain_entry.entry_type == DomainEntry.TYPE_A:
                return domain_entry.__str__()
        for domain_entry in self.domains:
            if query.endswith(domain_entry.domain) and domain_entry.entry_type == DomainEntry.TYPE_NS:
                return domain_entry.__str__()
        return NO_DOMAIN_ENTRY_STR


def main():
    if len(argv) < 3:
        print("Usage: python server.py <myPort> <zoneFileName>")
        sys.exit()

    port = int(argv[1])
    domain_file_name = argv[2]

    if port < 0 or port > 65535:
        print("Port number must be in range 0-65535")
        sys.exit()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))

    domain_list = DomainList()

    try:
        with open(domain_file_name, 'r') as file:
            for line in file:
                parts = line.split(',')
                if len(parts) == 3:
                    # parts[0] : domain name
                    # parts[1] : domain ip
                    # parts[2] : enty type
                    domain_list.add(
                        DomainEntry(parts[0], parts[1], parts[2])
                    )
    except Exception as e:
        print(f"Error reading domain file: {e}")
        sys.exit()

    while True:
        data, addr = s.recvfrom(1024)
        query = data.decode()
        answer = domain_list.resolve(query)
        s.sendto(answer.encode(), addr)


if __name__ == "__main__":
    main()
