import socket
import sys
from sys import argv

from domain import DomainList, DomainEntry

if __name__ == "__main__":

    if len(argv) < 3:
        print("Usage: python server.py <domain_file> <port>")
        sys.exit()

    domain_file_name = argv[1]
    port = int(argv[2])

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
        answer = domain_list.resolve(str(data))
        s.sendto(answer, addr)