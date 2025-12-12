import socket
import sys
import os


def main():
    # Check argument amount
    if len(sys.argv) < 3:
        return

    server_ip = sys.argv[1]
    server_port = int(sys.argv[2])

    # Infinite loop to get paths from the user
    while True:
        try:
            path = input()
        except EOFError:
            break

        # Create a TCP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        try:
            # Connect to the server
            sock.connect((server_ip, server_port))

            # We create the GET request for the file and send it to the server
            # We close the connection right after.
            request = (
                f"GET {path} HTTP/1.1\r\n"
                f"Host: {server_ip}:{server_port}\r\n"
                f"Connection: close\r\n"
                f"\r\n"
            )

            sock.sendall(request.encode())

            # Get back the response data
            response_data = b""
            while True:
                chunk = sock.recv(4096)
                if not chunk:
                    break
                response_data += chunk

            sock.close()

            # Get the header and body parts by splitting on two newlines
            parts = response_data.split(b'\r\n\r\n', 1)

            header_bytes = parts[0]

            # Print the first line of the response
            first_line = header_bytes.decode('utf-8', errors='ignore').split('\r\n')[0]
            print(first_line)

            # In case of 200 response, we will save the body content to a file
            # we will get the filename from the path
            if len(parts) > 1:
                body_content = parts[1]

                if "200 OK" in first_line:
                    filename = os.path.basename(path)

                    # if the path is / or empty, name it index.html
                    if not filename:
                        filename = "index.html"

                    # Save the body content to the file
                    with open(filename, "wb") as f:
                        f.write(body_content)

        except Exception as e:
            # If there was an error we close the connection
            if sock:
                sock.close()


if __name__ == "__main__":
    main()