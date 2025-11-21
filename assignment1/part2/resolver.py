import socket
import sys
from sys import argv
import time

from server import DomainList, DomainEntry, NO_DOMAIN_ENTRY_STR


def resolve_ns_record(s: socket.socket, domain_list: DomainList, cache_time: int, ip_str: str, query: str) -> str:
    """
    Resolve an NS record by querying the nameserver specified in ip_str.
    This function sends the query to the nameserver and processes the response.
    If the response is an A record, it adds it to the domain list and returns the
    answer. If the response is another NS record, it continues querying the new nameserver.
    """
    # Unpack the IP and port from the ip_str
    current_ns_ip, current_port_str = ip_str.split(':')
    current_port = int(current_port_str)

    # While loop to handle multiple NS records
    while True:
        # Send the query to the current server
        s.sendto(query.encode(), (current_ns_ip, current_port))

        # Get the answer from the server
        ns_answer_bytes, _ = s.recvfrom(1024)
        answer = ns_answer_bytes.decode()

        # If the answer is NO_DOMAIN_ENTRY_STR, break the loop
        if answer == NO_DOMAIN_ENTRY_STR:
            break

        # Else, parse the answer
        parts = answer.split(',')

        # If it is not a valid entry, break the loop
        if len(parts) != 3:
            break

        # Parse the parts
        domain, ip, entry_type = parts[0], parts[1], parts[2]

        # Set expire time and add to domain list
        expire_time = None
        if cache_time > 0:
            expire_time = time.time() + cache_time
        domain_list.add(DomainEntry(domain, ip, entry_type, expire_time))

        # If it is an A record, return the answer
        if entry_type == DomainEntry.TYPE_A:
            break

        # If it is an NS record, update the current_ns_ip and current_port
        elif entry_type == DomainEntry.TYPE_NS:
            current_ns_ip, current_port_str = ip.split(':')
            current_port = int(current_port_str)

    return answer


def main():
    # Check the amount of command line arguments
    if len(argv) < 5:
        # print("Usage: python resolver.py <myPort> <parentIP> <parentPort> <cacheTime>")
        sys.exit()

    # Move the command line arguments into variables
    port = int(argv[1])
    parent_ip = argv[2]
    parent_port = int(argv[3])
    cache_time = int(argv[4])

    # Check that port numbers are valid
    if port < 0 or port > 65535:
        # print("Port number must be in range 0-65535")
        sys.exit()

    if parent_port < 0 or parent_port > 65535:
        # print("Parent port number must be in range 0-65535")
        sys.exit()

    # Create UDP socket and bind to the specified port
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.bind(('', port))

    # Create DomainList
    domain_list = DomainList()

    while True:
        # Receive a query from a client and try to resolve it
        data, addr = s.recvfrom(1024)
        query = data.decode()
        answer = domain_list.resolve(query)

        # If the answer is not NO_DOMAIN_ENTRY_STR, check if it is an NS entry
        if answer != NO_DOMAIN_ENTRY_STR:
            # check if it is an NS entry
            parts = answer.split(',')
            if len(parts) == 3:
                ip, entry_type = parts[1], parts[2]
                # For NS entries, we need to resolve the A record from the parent server
                if entry_type == DomainEntry.TYPE_NS:
                    # If it is an NS entry, resolve it with the correct function
                    answer = resolve_ns_record(s, domain_list, cache_time, ip, query)

        # If the answer is NO_DOMAIN_ENTRY_STR, forward the request to the parent server
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
                    # Set expire time and add to domain list
                    expire_time = None
                    if cache_time > 0:
                        expire_time = time.time() + cache_time
                    domain_list.add(DomainEntry(domain, ip, entry_type, expire_time))

                    # For NS entries, we need to resolve the A record from the parent server
                    if entry_type == DomainEntry.TYPE_NS:
                        answer = resolve_ns_record(s, domain_list, cache_time, ip, query)

        # Send the answer back to the client
        s.sendto(answer.encode(), addr)


if __name__ == "__main__":
    main()
