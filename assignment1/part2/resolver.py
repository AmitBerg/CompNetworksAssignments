import socket
import sys
from sys import argv
import time

from domain import DomainList, DomainEntry, NO_DOMAIN_ENTRY_STR

if __name__ == "__main__":

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

        if answer == NO_DOMAIN_ENTRY_STR:
            # Forward the request to the parent server
            # print("Forwarding request to parent server at {}:{}".format(parent_ip, parent_port))
            s.sendto(data, (parent_ip, parent_port))
            parent_answer, _ = s.recvfrom(1024)
            answer = parent_answer.decode()

            # Cache the response if it's not a non-existent domain
            if answer != NO_DOMAIN_ENTRY_STR:
                parts = answer.split(',')
                if len(parts) == 3:
                    domain = parts[0]
                    ip = parts[1]
                    entry_type = parts[2]
                    expire_time = None
                    if cache_time > 0:
                        expire_time = time.time() + cache_time
                    domain_list.add(DomainEntry(domain, ip, entry_type, expire_time))

        s.sendto(answer.encode(), addr)


# print("domain: {}, ip: {}, entry_type: {}".format(domain, ip, entry_type))
#
# while entry_type is not DomainEntry.TYPE_A:
#     # For NS entries, send another request to get the A record from the server
#     # with address 'ip'
#     print("Trying to resolve NS entry for domain: {}, ip: {}, entry_type: {}".format(domain, ip, entry_type))
#     ns_ip, port = ip.split(':')
#     port = int(port)
#     s.sendto(query.encode(), (ns_ip, port))
#     parent_answer, _ = s.recvfrom(1024)
#     answer = parent_answer.decode()
#     parts = answer.split(',')
#     if len(parts) != 3:
#         break
#     domain = parts[0]
#     ip = parts[1]
#     entry_type = parts[2]