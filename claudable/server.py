#!/usr/bin/env python3
import http.server
import socketserver
import os

PORT = 7860
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        self.send_header('Expires', '0')
        super().end_headers()

if __name__ == "__main__":
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"Server running at http://127.0.0.1:{PORT}/")
        print(f"Serving files from: {DIRECTORY}")
        print(f"Open http://127.0.0.1:{PORT}/index.html")
        httpd.serve_forever()
