import discord_oauth2, json, requests
from http.server import BaseHTTPRequestHandler
from Global import Client, secret

name = "0.0.0.0"
port = 3080

user_count   = 0
server_count = 0

discord_API_version = 10

OAuth2 = discord_oauth2.DiscordAuth(Client.user.id, secret, "https://pzazs.thatgalblu.com/api/login/callback")
login_redirect = fr"https://discord.com/oauth2/authorize?client_id={Client.user.id}&response_type=code&redirect_uri=https%3A%2F%2Fpzazs.thatgalblu.com%2Fapi%2Flogin%2Fcallback&scope=identify+guilds"


class Server(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        # Spliting URL path and parameters
        url = self.path.removeprefix('/').removesuffix('/').split('?')[0].split('/')
        parameters = {}; pairs = self.path.split('?').pop().split('&')
        for pair in pairs:
            pair = pair.split('=') + [True]
            parameters[pair[0]] = pair[1]

        # Generate a response based on the URL given
        headers, status, data = self.handle_GET_request_response(url, parameters)
        
        self.send_response(status)
        self.send_header("Access-Control-Allow-Origin", "*")
        for header in headers: self.send_header(*header)
        self.end_headers()
        if isinstance(data, (dict, list)): data = bytes(json.dumps(data), 'utf-8')
        self.wfile.write(data)

    
    def handle_GET_request_response(self, url: list[str], parameters: dict) -> list[list[tuple[str, str]], int, dict]:
        # Returns are formated as headers, status_code, and data. Errors are handled as unpacked (status_code, data)
        if url[0] == "api":
            headers = [("Content-Type", "application/json")]

            # Returns the data from the Client that's updated in /threads/update_api.py
            if len(url) == 1: return headers, 200, {"userCount": user_count, "serverCount": server_count}

            # Returns the HTTP user's shared guilds with the Client
            elif url[1] == "getguilds":
                try: token = parameters['token']
                except: return headers, *error(401, "No API key/access token provided.")
                try: guilds = fetch("/guilds", token)
                except: return headers, *error(401, "Invalid API key/access token.")

                client_guild_IDs = [guild.id for guild in Client.guilds]
                return headers, 200, [guild for guild in guilds if int(guild['id']) in client_guild_IDs]

            # Returns files from /http/res
            elif url[1] == "res":
                url = "/".join(url); assert isinstance(url, str)
                try:
                    with open(f"./http{url.removeprefix('api')}", "rb") as data: return [], 200, data.read()
                except: return [("Content-Type", "application/json")], *error(404, f"File \"./{url}\" not found.")

            elif url[1] == "login":
                if len(url) == 2: return [("Location", login_redirect)], 307, bytes("", 'utf-8')

                if url[2] == "callback":
                    try:
                        data = OAuth2.get_tokens(parameters['code'])
                        headers = [("Set-Cookie", f"discord_access_token={data['access_token']}; Domain=pzazs.thatgalblu.com; Path=/")]
                    except: return [("Content-Type", "application/json")], *error(400, "Unable to get Discord user access token.")
                    else:
                        headers.append(("Location", "https://pzazs.thatgalblu.com"))
                    
                        return headers, 308, bytes("", 'utf-8')
                    
        return [], 404, bytes("", 'utf-8')

    # Disable the HTTP logs
    def log_message(self, format, *args): pass

# Fetch from the Discord Rest API, with path
def fetch(address: str, access_token: str) -> dict:
    response = requests.get(f"https://discord.com/api/v{discord_API_version}/users/@me{address}", headers={"Authorization": f"Bearer {access_token}"})
    return response.json()

# Error builder for sending out to user
def error(status: int, reason: str) -> tuple[int, dict]: return status, {"error": status, "reason": reason}