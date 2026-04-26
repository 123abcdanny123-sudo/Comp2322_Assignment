import socket


class WebClient:
    def __init__(self, host='127.0.0.1', port=8080):
        self.host = host
        self.port = port

    def send_raw_request(self, request_string):
        """Helper to send a raw string and return the response."""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((self.host, self.port))
            s.sendall(request_string.encode())

            response = b""
            while True:
                data = s.recv(4096)
                if not data:
                    break
                response += data
            return response.decode(errors='ignore')

    def test_get_success(self):
        print("--- Testing 200 OK (GET) ---")
        request = "GET /index.html HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"
        print(self.send_raw_request(request))

    def test_head_command(self):
        print("--- Testing HEAD Command ---")
        request = "HEAD /index.html HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"
        print(self.send_raw_request(request))

    def test_404_not_found(self):
        print("--- Testing 404 File Not Found ---")
        request = "GET /nonexistent.html HTTP/1.1\r\nHost: 127.0.0.1\r\n\r\n"
        print(self.send_raw_request(request))

    def test_400_bad_request(self):
        print("--- Testing 400 Bad Request ---")
        request = "NOT_A_METHOD /index.html\r\n\r\n"
        print(self.send_raw_request(request))

    def test_caching_304(self):
        print("--- Testing 304 Not Modified ---")
        request = (
            "GET /index.html HTTP/1.1\r\n"
            "Host: 127.0.0.1\r\n"
            "If-Modified-Since: Wed, 21 Oct 2026 07:28:00 GMT\r\n\r\n"
        )
        print(self.send_raw_request(request))


if __name__ == "__main__":
    client = WebClient()

    # tests
    client.test_get_success()
    client.test_head_command()
    client.test_404_not_found()
    client.test_400_bad_request()
    client.test_caching_304()