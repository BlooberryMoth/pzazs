from Global import LOGGER
from http.server import HTTPServer
from APIServer import name, port, Server


def execute():
    server = HTTPServer((name, port), Server)
    
    LOGGER.info(f"Starting HTML server at \"http://{name}:{port}\"...")
    try: server.serve_forever()
    except KeyboardInterrupt: server.server_close()
    LOGGER.info("HTML server stopped.")