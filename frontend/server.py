"""
Simple HTTP server to serve CyberGuardX frontend on port 3000
Run this script from the frontend directory
"""

import http.server
import socketserver
import os

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    # Ensure .js files are served with correct MIME type for ES modules
    extensions_map = {
        **http.server.SimpleHTTPRequestHandler.extensions_map,
        '.js': 'application/javascript',
        '.mjs': 'application/javascript',
        '.css': 'text/css',
        '.json': 'application/json',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)
    
    def end_headers(self):
        self.send_header('Cache-Control', 'no-store, no-cache, must-revalidate')
        super().end_headers()

if __name__ == '__main__':
    os.chdir(DIRECTORY)
    
    with socketserver.TCPServer(("", PORT), MyHTTPRequestHandler) as httpd:
        print(f"╔════════════════════════════════════════╗")
        print(f"║   CyberGuardX Frontend Server          ║")
        print(f"╚════════════════════════════════════════╝")
        print(f"\n✓ Server running at: http://localhost:{PORT}")
        print(f"✓ Serving files from: {DIRECTORY}")
        print(f"\n⚡ Open your browser and navigate to: http://localhost:{PORT}")
        print(f"\n⚠️  Make sure the backend is running at: http://localhost:8000")
        print(f"\nPress Ctrl+C to stop the server\n")
        
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\n\n✓ Server stopped.")
