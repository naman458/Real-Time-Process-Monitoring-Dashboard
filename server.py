# server.py - Simple backend to provide real process data
import http.server
import socketserver
import json
import psutil
import time
from urllib.parse import urlparse

PORT = 8000

class ProcessHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        # Enable CORS
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        
        # Parse the URL
        parsed_url = urlparse(self.path)
        
        # Check if this is a processes request
        if parsed_url.path == '/processes':
            # Get CPU and memory usage
            cpu_usage = psutil.cpu_percent()
            memory_usage = psutil.virtual_memory().percent
            
            # Get process information
            processes_info = []
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 'status']):
                try:
                    proc_info = proc.info
                    status = "Running" if proc_info['status'] == psutil.STATUS_RUNNING else "Sleeping"
                    processes_info.append({
                        'pid': proc_info['pid'],
                        'name': proc_info['name'],
                        'cpu': round(proc_info['cpu_percent'], 1),
                        'memory': round(proc_info['memory_percent'], 1),
                        'status': status
                    })
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    pass
            
            # Sort processes by CPU usage (highest first)
            processes_info.sort(key=lambda x: float(x['cpu']), reverse=True)
            
            # Limit to top 15 processes
            processes_info = processes_info[:15]
            
            # Create response
            response = {
                'cpu_usage': round(cpu_usage, 1),
                'memory_usage': round(memory_usage, 1),
                'processes': processes_info
            }
            
            # Send response
            self.wfile.write(json.dumps(response).encode())
        else:
            # Return empty response for other paths
            self.wfile.write(json.dumps({}).encode())

if __name__ == "__main__":
    print(f"Starting server at http://localhost:{PORT}")
    print("Make sure you have psutil installed (pip install psutil)")
    
    # Start server
    with socketserver.TCPServer(("", PORT), ProcessHandler) as httpd:
        print("Server running. Press Ctrl+C to stop.")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("Server stopped.")
