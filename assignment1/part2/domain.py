from typing import List
import time

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

