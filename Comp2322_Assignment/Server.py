import socket
import threading
import os
import time
from datetime import datetime


class WebServer:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port
        self.log_file = "server_log.txt"
        # Create server socket
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_socket.bind((self.host, self.port))

    def start(self):
        """Starts the server and listens for connections."""
        self.server_socket.listen(5)
        print(f"Server started on {self.host}:{self.port}")
        while True:
            client_socket, addr = self.server_socket.accept()
            client_thread = threading.Thread(target=self.handle_request, args=(client_socket, addr))
            client_thread.start()

    def handle_request(self, client_socket, addr):
        """Main thread function to handle HTTP logic."""
        try:
            raw_request = client_socket.recv(4096).decode('utf-8', errors='ignore')
            if not raw_request:
                client_socket.close()
                return

            #parse request
            lines = raw_request.split('\r\n')
            request_line = lines[0].split()

            if len(request_line) < 3:
                self.send_response(client_socket, "400 Bad Request", "text/html", "<h1>400 Bad Request</h1>", addr,
                                   "N/A")
                return

            method, path, _ = request_line
            filename = path.lstrip('/') if path != '/' else 'index.html'

            #check GET & HEAD
            if method not in ['GET', 'HEAD']:
                self.send_response(client_socket, "400 Bad Request", "text/html", "<h1>Method Not Allowed</h1>", addr,
                                   filename)
                return

            # 3. file system logic & status codes
            if not os.path.exists(filename):
                self.send_response(client_socket, "404 File Not Found", "text/html", "<h1>404 Not Found</h1>", addr,
                                   filename)
            elif os.access(filename, os.R_OK) is False:
                self.send_response(client_socket, "403 Forbidden", "text/html", "<h1>403 Forbidden</h1>", addr,
                                   filename)
            else:
                # handle (304 Not Modified)
                self.serve_file(client_socket, method, filename, addr)

        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()

    def serve_file(self, client_socket, method, filename, addr):
        """Reads file in binary and sends response[cite: 17, 18, 58]."""
        mode = 'rb'
        content_type = "image/jpeg" if filename.endswith(('.jpg', '.jpeg')) else "text/html"

        with open(filename, mode) as f:
            content = f.read()

        # HEAD command: Same headers, but NO body
        body = b"" if method == 'HEAD' else content
        self.send_response(client_socket, "200 OK", content_type, body, addr, filename)

    def send_response(self, client_socket, status, content_type, body, addr, filename):
        """Constructs proper HTTP response message."""
        header = f"HTTP/1.1 {status}\r\n"
        header += f"Content-Type: {content_type}\r\n"
        header += f"Content-Length: {len(body)}\r\n"
        header += "Connection: close\r\n\r\n"  # Non-persistent for now [cite: 63]

        response = header.encode('utf-8')
        if isinstance(body, str):
            response += body.encode('utf-8')
        else:
            response += body  # Bytes for images

        client_socket.sendall(response)
        self.write_log(addr, filename, status)

    def write_log(self, addr, filename, status):
        """Requirement: Log client IP, time, filename, and response type[cite: 26, 27, 70]."""
        with open(self.log_file, "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            log_entry = f"{addr[0]}, {timestamp}, {filename}, {status}\n"
            f.write(log_entry)


if __name__ == "__main__":
    server = WebServer()
    server.start()

