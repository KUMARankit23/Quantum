#!/usr/bin/env python3
"""
Simple HTTP Server to serve the dashboard on port 3000
"""
import http.server
import socketserver
import os
import webbrowser
from pathlib import Path

PORT = 3000
DASHBOARD_DIR = Path(__file__).parent

class DashboardHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # If root path, serve FRQI animated dashboard
        if self.path == '/':
            self.path = '/dashboard_frqi_animated.html'
        return super().do_GET()
    
    def log_message(self, format, *args):
        # Suppress verbose logging
        pass

def run_server():
    os.chdir(DASHBOARD_DIR)
    
    with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
        print(f"""
╔════════════════════════════════════════════╗
║   Quantum Dashboard Server Running         ║
╚════════════════════════════════════════════╝

✓ Server: http://localhost:{PORT}
✓ Dashboard: http://localhost:{PORT}/dashboard.html
✓ Status: Ready

Press Ctrl+C to stop server
""")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n✓ Server stopped")

if __name__ == '__main__':
    run_server()
