from typing import List

NO_DOMAIN_ENTRY_STR = "non-existent domain"

class DomainEntry:
    TYPE_NS = "NS"
    TYPE_A = "A"
    def __init__(self, domain: str, ip: str, entry_type: str):
        self.domain = domain
        self.ip = ip
        self.entry_type = entry_type

    def __str__(self):
        return f"{self.domain},{self.ip},{self.entry_type}"

class DomainList:
    def __init__(self):
        self.domains : List[DomainEntry] = []

    def add(self, entry: DomainEntry):
        self.domains.append(entry)

    def resolve(self, query: str) -> str:
        for domain_entry in self.domains:
            if domain_entry.entry_type == query and domain_entry.entry_type == DomainEntry.TYPE_A:
                return domain_entry.__str__()
        for domain_entry in self.domains:
            if query.endswith(domain_entry.domain) and domain_entry.entry_type == DomainEntry.TYPE_NS:
                return domain_entry.__str__()
        return NO_DOMAIN_ENTRY_STR