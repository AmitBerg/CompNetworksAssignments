import socket
import sys
from sys import argv
import time

from domain import DomainList, DomainEntry, NO_DOMAIN_ENTRY_STR


def resolve_ns_record(s: socket.socket, domain_list: DomainList, cache_time: int, ip_str: str, query: str) -> str:
    current_ns_ip, current_port_str = ip_str.split(':')
    current_port = int(current_port_str)

    while True:
        s.sendto(query.encode(), (current_ns_ip, current_port))

        ns_answer_bytes, _ = s.recvfrom(1024)
        answer = ns_answer_bytes.decode()

        if answer == NO_DOMAIN_ENTRY_STR:
            break

        parts = answer.split(',')

        if len(parts) != 3:
            break

        domain, ip, entry_type = parts[0], parts[1], parts[2]

        expire_time = None
        if cache_time > 0:
            expire_time = time.time() + cache_time
        domain_list.add(DomainEntry(domain, ip, entry_type, expire_time))

        if entry_type == DomainEntry.TYPE_A:
            break

        elif entry_type == DomainEntry.TYPE_NS:
            current_ns_ip, current_port_str = ip.split(':')
            current_port = int(current_port_str)

    return answer

def main():
    if len(argv) < 5:
        print("Usage: python resolver.py <myPort> <parentIP> <parentPort> <cacheTime>")
        sys.exit()

    port = int(argv[1])
    parent_ip = argv[2]
    parent_port = int(argv[3])
    cache_time = int(argv[4])

    if port < 0 or port > 65535:
        print("Port number must be in range 0-65535")
        sys.exit()

    if parent_port < 0 or parent_port > 65535:
        print("Parent port number must be in range 0-65535")
        sys.exit()

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))

    domain_list = DomainList()

    while True:
        data, addr = s.recvfrom(1024)
        query = data.decode()
        answer = domain_list.resolve(query)

        if answer != NO_DOMAIN_ENTRY_STR:
            # check if it is an NS entry
            parts = answer.split(',')
            if len(parts) == 3:
                ip, entry_type = parts[1], parts[2]
                # For NS entries, we need to resolve the A record from the parent server
                if entry_type == DomainEntry.TYPE_NS:
                    answer = resolve_ns_record(s, domain_list, cache_time, ip, query)

        elif answer == NO_DOMAIN_ENTRY_STR:
            # Forward the request to the parent server
            s.sendto(data, (parent_ip, parent_port))
            parent_answer, _ = s.recvfrom(1024)
            answer = parent_answer.decode()

            # Cache the response if it's not a non-existent domain
            if answer != NO_DOMAIN_ENTRY_STR:
                parts = answer.split(',')
                if len(parts) == 3:
                    domain, ip, entry_type = parts[0], parts[1], parts[2]
                    expire_time = None
                    if cache_time > 0:
                        expire_time = time.time() + cache_time
                    domain_list.add(DomainEntry(domain, ip, entry_type, expire_time))

                    # For NS entries, we need to resolve the A record from the parent server
                    if entry_type == DomainEntry.TYPE_NS:
                        answer = resolve_ns_record(s, domain_list, cache_time, ip, query)

        s.sendto(answer.encode(), addr)

if __name__ == "__main__":
    main()
