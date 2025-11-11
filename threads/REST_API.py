from http.server import HTTPServer, BaseHTTPRequestHandler
from website import HTTPHandler
from Logging import LOG
import re

PORT = 3080 # Assign your port here


class Server(BaseHTTPRequestHandler):
    with open('./website/http/404/index.html') as file_in: index = file_in.buffer.read()
    fourohfour = 404, [], index # This variable is for the default 404 page in "/http/404"

    def do_GET(self) -> None:
        url, pairs, *_ = self.path.split('?') + [""]
        if re.search("^([^.]*[^/])$", url): return self.send_data(308, [("Location", f'./{url.split("/")[-1]}/{("?" + pairs) if pairs else ""}')], "")
        url = url.removeprefix('/').removesuffix('/')
        parameters = {}
        for pair in pairs.split('&'):
            pair = pair.split('=') + [True]
            parameters[pair[0]] = pair[1]

        status, headers, data = HTTPHandler.handle_GET_request(["."] + url.split('/'), parameters)
        self.send_data(status, headers, data)


    def do_POST(self) -> None:
        body = self.rfile.read(int(self.headers['Content-Length']))

        status, headers, data = HTTPHandler.handle_POST_request(body)
        self.send_data(status, headers, data)


    def send_data(self, status, headers, data) -> None:
        self.send_response(status)
        for header in headers: self.send_header(*header)
        self.end_headers()
        if not isinstance(data, (bytes, bytearray)): data = bytes(data, 'utf-8')
        self.wfile.write(data)

    def log_message(self, format, *args): pass


def execute():
    LOG.info("Opening HTTP Server.")
    server = HTTPServer(("0.0.0.0", PORT), Server)
    try: server.serve_forever()
    except KeyboardInterrupt: pass
    except Exception as e: LOG.critical(e)
    LOG.warning("Closed HTTP Server.")