import socket
import sys
import os

def main():
    # Check argument amount
    if len(sys.argv) < 2:
        print("Usage: python server.py <port>")
        return

    server_port = int(sys.argv[1])

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Allow the socket to reuse the address
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    try:
        server_socket.bind(('', server_port))
        server_socket.listen(5)
        # Allow us to press ctrl C in order to stop the program
        server_socket.settimeout(0.5)
        print(f"Server is listening on port {server_port}...")
    except Exception as e:
        print(f"Error starting server: {e}")
        return

    while True:
        try:
            try:
                # Accept a new connection
                client_socket, client_address = server_socket.accept()
            except socket.timeout:
                # Allow us to press ctrl C in order to stop the program
                continue
            except OSError:
                break

            # Configure a timeout of 1 second for client socket
            client_socket.settimeout(1.0)
            # Handle the client connection
            handle_client_connection(client_socket)

        except KeyboardInterrupt:
            print("\nServer stopping...")
            break
        except Exception as e:
            print(f"Server error: {e}")
            continue

    server_socket.close()


def handle_client_connection(client_socket):
    """
    Handles the client connection, processing multiple requests if keep-alive is used.
    """
    while True:
        try:
            # Read the request data
            try:
                request_data = client_socket.recv(4096)
            except socket.timeout:
                # if there is a timeout, close the connection
                client_socket.close()
                return
            except Exception:
                client_socket.close()
                return

            # If there was no data received, close the connection
            if not request_data:
                client_socket.close()
                return

            request_str = request_data.decode('utf-8', errors='ignore')

            # Print the request
            print(request_str)

            lines = request_str.split('\r\n')
            if not lines:
                client_socket.close()
                return

            request_line = lines[0].split()

            if len(request_line) < 2:
                client_socket.close()
                return

            path = request_line[1]

            # Test if the type of connection the client wants, default is keep-alive
            connection_header_val = "keep-alive"
            for line in lines:
                if line.lower().startswith("connection:"):
                    if "close" in line.lower():
                        connection_header_val = "close"
                    elif "keep-alive" in line.lower():
                        connection_header_val = "keep-alive"
                    break


            # Redirect case
            if path == "/redirect":
                # We redirect to /result.html and close the connection
                response = (
                    "HTTP/1.1 301 Moved Permanently\r\n"
                    "Connection: close\r\n"
                    "Location: /result.html\r\n"
                    "\r\n"
                )
                client_socket.sendall(response.encode())
                client_socket.close()
                return

            # Home page case
            if path == "/":
                filename = "index.html"
            else:
                if path.startswith("/"):
                    filename = path[1:]
                else:
                    filename = path

            # Otherwise, extract the file from the files directory
            file_path = os.path.join("files", filename)

            # Check if such file exists
            if os.path.isfile(file_path):
                filesize = os.path.getsize(file_path)

                # Read the file content
                with open(file_path, "rb") as f:
                    file_content = f.read()

                # Send 200 OK response with file content and set the connection header as the same we had before
                header = (
                    f"HTTP/1.1 200 OK\r\n"
                    f"Connection: {connection_header_val}\r\n"
                    f"Content-Length: {filesize}\r\n"
                    f"\r\n"
                )

                client_socket.sendall(header.encode() + file_content)

                # if the client wanted to close the connection, we close it
                # if the connection type wanted was keep alive, we just stay in the loop
                if connection_header_val == "close":
                    client_socket.close()
                    return

            else:
                # If the file does not exist, return 404 and close the connection
                response = (
                    "HTTP/1.1 404 Not Found\r\n"
                    "Connection: close\r\n"
                    "\r\n"
                )
                client_socket.sendall(response.encode())
                client_socket.close()
                return

        except Exception:
            client_socket.close()
            return


if __name__ == "__main__":
    main()