import discord_oauth2, json, logging
from http.server import BaseHTTPRequestHandler
from typing import *
from Global import Client, secret

name = "0.0.0.0"
port = 3080

iconURL     = "./api/res/images/404.png"
userCount   = 0
serverCount = 0

OAuth2 = discord_oauth2.DiscordAuth(Client.user.id, secret, "https://pzazs.thatgalblu.com/api/login/callback")
loginRedirect = fr"https://discord.com/oauth2/authorize?client_id={Client.user.id}&response_type=code&redirect_uri=https%3A%2F%2Fpzazs.thatgalblu.com%2Fapi%2Flogin%2Fcallback&scope=identify+guilds"

logging.getLogger("requests").setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)


class Server(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        url = self.path.removeprefix('/').removesuffix('/').split('/')

        headers, status, data = self.handle_GET_request_response(url)
        
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        for header in headers: self.send_header(*header)
        self.end_headers()
        if isinstance(data, dict): data = bytes(json.dumps(data), 'utf-8')
        self.wfile.write(data)

    
    def handle_GET_request_response(self, url: list) -> list[list[tuple[str, str]], int, dict]:
        headers = []
        if url[0] == "api":
            headers.append(("Content-Type", "application/json"))

            if len(url) == 1: return headers, 200, {"iconURL": iconURL.split('?')[0], "userCount": userCount, "serverCount": serverCount}
            elif url[1] == "stats":
                try: serverID = url[2]
                except: return headers, *error(400, "Unable to parse server ID from URL.")

                if len(url) >= 3:
                    try:
                        with open(f'./res/statistics/{serverID}.json') as data: return headers, 200, data
                    except: return headers, *error(404, f"File \"{serverID}.json\" not found.")

            elif url[1] == "res":
                url = "/".join(url)
                if url.endswith('png'): headers = [("Content-Type", "image/png")]
                elif url.endswith(('jpeg', 'jpg')): headers = [("Content-Type", "image/jpeg")]
                try:
                    with open(f".{url.removeprefix('api')}", "rb") as data: return headers, 200, data.read()
                except: return [("Content-Type", "application/json")], *error(404, f"File \"./{url}\" not found.")

            elif url[1] == "login":
                if len(url) == 2: return [("Location", loginRedirect)], 307, bytes("", 'utf-8')

                if url[2].startswith('callback'):
                    code = url[2].split('?')[1].split('=')[1]

                    try:
                        data = OAuth2.get_tokens(code)
                        headers = [("Set-Cookie", f"discord_access_token={data['access_token']}; Domain=pzazs.thatgalblu.com")]
                    except: return [("Content-Type", "application/json")], *error(400, "Unable to get Discord user access token.")
                    else:
                        headers.append(("Location", "https://pzazs.thatgalblu.com"))
                    
                        return headers, 308, bytes("", 'utf-8')
                    
        return headers, 404, bytes("", 'utf-8')


def error(status: int, reason: str) -> tuple[int, dict]: return status, {"error": status, "reason": reason}