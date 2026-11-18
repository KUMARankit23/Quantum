#!/usr/bin/env python3
"""
Quantum Image Processing System Launcher
Starts both the FastAPI backend and HTML dashboard frontend
"""

import subprocess
import sys
import time
import os
from pathlib import Path
import threading
import webbrowser

def is_port_available(port):
    """Check if a port is available"""
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('localhost', port))
            return True
        except OSError:
            return False

def run_api_server():
    """Run the FastAPI backend server"""
    print("\n" + "="*70)
    print("Starting Quantum Image Processing API Server (Port 8000)")
    print("="*70)
    print("\nEndpoints available:")
    print("  - POST /process/frqi     (Process with FRQI encoding)")
    print("  - POST /process/neqr     (Process with NEQR encoding)")
    print("  - POST /compare          (Compare both methods)")
    print("  - GET /health            (Health check)")
    print("  - GET /docs              (API documentation)")
    print("\n")
    
    try:
        subprocess.run([sys.executable, "quantum_api_server.py"], cwd=Path(__file__).parent)
    except KeyboardInterrupt:
        print("\n✓ API Server stopped")
        return
    except Exception as e:
        print(f"\n✗ Error running API server: {e}")
        return

def run_dashboard_server():
    """Run the HTML dashboard server"""
    # Wait for API to start
    time.sleep(2)
    
    print("\n" + "="*70)
    print("Starting Dashboard Server (Port 3000)")
    print("="*70)
    print("\nDashboard available at: http://localhost:3000")
    print("\n")
    
    os.chdir(Path(__file__).parent)
    
    try:
        import http.server
        import socketserver
        
        PORT = 3000
        
        class DashboardHandler(http.server.SimpleHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.path = '/dashboard_research.html'
                return super().do_GET()
            
            def log_message(self, format, *args):
                pass  # Suppress logging
        
        with socketserver.TCPServer(("", PORT), DashboardHandler) as httpd:
            print(f"✓ Dashboard server ready on http://localhost:{PORT}")
            print("\nPress Ctrl+C to stop both servers\n")
            httpd.serve_forever()
            
    except KeyboardInterrupt:
        print("\n✓ Dashboard Server stopped")
        return
    except Exception as e:
        print(f"\n✗ Error running dashboard server: {e}")
        return

def main():
    """Main launcher"""
    print("\n")
    print("╔" + "="*68 + "╗")
    print("║" + " "*68 + "║")
    print("║" + "  ⚛️  QUANTUM IMAGE PROCESSING RESEARCH SYSTEM  ⚛️".center(68) + "║")
    print("║" + "  Real-time FRQI vs NEQR Comparison Dashboard".center(68) + "║")
    print("║" + " "*68 + "║")
    print("╚" + "="*68 + "╝\n")

    # Check dependencies
    print("📋 Checking dependencies...")
    try:
        import fastapi
        import uvicorn
        import qiskit
        import qiskit_aer
        print("✓ All required packages installed\n")
    except ImportError as e:
        print(f"\n✗ Missing package: {e}")
        print("\nInstall requirements with:")
        print("  pip install -r requirements.txt\n")
        sys.exit(1)

    # Check ports
    print("🔍 Checking port availability...")
    if not is_port_available(8000):
        print("✗ Port 8000 is already in use. Close the application using it and try again.")
        sys.exit(1)
    
    if not is_port_available(3000):
        print("✗ Port 3000 is already in use. Close the application using it and try again.")
        sys.exit(1)
    
    print("✓ Ports 3000 and 8000 are available\n")

    # Start servers in threads
    api_thread = threading.Thread(target=run_api_server, daemon=False)
    dashboard_thread = threading.Thread(target=run_dashboard_server, daemon=False)

    try:
        api_thread.start()
        dashboard_thread.start()
        
        # Wait for dashboard to start, then open browser
        time.sleep(4)
        try:
            print("\n🌐 Opening dashboard in browser...")
            webbrowser.open('http://localhost:3000')
        except:
            print("\n✓ Please open http://localhost:3000 in your browser")
        
        # Keep main thread alive
        api_thread.join()
        dashboard_thread.join()
        
    except KeyboardInterrupt:
        print("\n\n" + "="*70)
        print("Shutting down Quantum Image Processing System...")
        print("="*70)
        print("\nThank you for using the Quantum Research Dashboard! 🔬\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
