from http.server import HTTPServer, BaseHTTPRequestHandler
import json
""" this simple http server was produced by AI to help recive the http post requests that my c2 server does it saves to the file hej.txt"""
class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(b'Hello, GET request received!')

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])  # Get the size of data
        post_data = self.rfile.read(content_length)  # Read the POST data
        print(f"Received POST data: {post_data.decode('utf-8')}")
        with open("cc.txt",'a') as file:
            file.write(post_data.decode('utf-8'))


        # Send a response
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()

        # Respond with a simple JSON message
        response = {
            'status': 'success',
            'message': 'POST request received'
        }
        self.wfile.write(json.dumps(response).encode('utf-8'))

# Set up the server
def serve(ip,port):
    
    httpd = HTTPServer((ip, port), SimpleHTTPRequestHandler)
    print('Starting server on port 8000...')
    httpd.serve_forever()
