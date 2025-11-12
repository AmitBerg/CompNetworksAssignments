import socket
import sys
from sys import argv

def main():
    # Check that the correct number of arguments are provided
    if len(argv) < 3:
        # print("Usage: python client.py <serverIP> <serverPort>")
        sys.exit()

    # Get the arguments into variables
    server_ip = argv[1]
    server_port = int(argv[2])

    # Check that the port number is valid
    if server_port < 0 or server_port > 65535:
        # print("Server port number must be in range 0-65535")
        sys.exit()

    # Create the UDP socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    try:
        while True:
            # Get the query from the user
            query = input()
            # Send the query to the server
            s.sendto(query.encode(), (server_ip, server_port))
            data, addr = s.recvfrom(1024)
            # Receive the answer from the server and print it
            answer = data.decode()
            parts = answer.split(',')
            if len(parts) == 3:
                ip = parts[1]
                print(ip)
            else:
                print(answer)
    except KeyboardInterrupt:
        pass

    s.close()

if __name__ == "__main__":
    main()
