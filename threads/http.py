from Global import log
from http.server import HTTPServer
from APIServer import name, port, Server


def execute():
    server = HTTPServer((name, port), Server)
    
    log(f"Starting HTML server at \"http://{name}:{port}\"...")
    try: server.serve_forever()
    except KeyboardInterrupt: server.server_close()
    log("HTML server stopped.")