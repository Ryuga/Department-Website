import httpx

url = "https://discord.com/api/v9"


class DiscordAPIClient:
    headers = {}

    def __init__(self, authorization):
        self.headers["Authorization"] = authorization

    def post(self, endpoint, data=None, files=None):
        try:
            resp = httpx.post(url+endpoint, headers=self.headers, data=data, files=files)
            return resp.json()
        except Exception as E:
            return

    def upload_file(self, bin_file):
        files = {
            "file": ("myqrcode.png", bin_file)
        }
        return self.post("/channels/892472876064702494/messages", data={"content": ""}, files=files)