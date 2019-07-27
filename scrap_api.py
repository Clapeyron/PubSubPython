import requests
from datetime import datetime


class Scraper:
    def __init__(self, token=None, api_path="https://api.clapeyronrobotics.com"):
        self.TOKEN = token
        self.HEADERS = {"Authorization": f"RClap {token}"}
        self.API_PATH = api_path
        self.USER = self._current_user()
        self.USER_ID = self.USER["user_id"]
        self.ROLE = self.USER["role"]
        self.last_point = datetime.utcnow()

    def api_request(self, method, local_url, body=None, headers=None):
        if headers is None: headers = self.HEADERS
        resp = getattr(requests, method)(f"{self.API_PATH}/{local_url}", headers=headers, json=body)
        if resp.status_code == 200:
            return resp.json()
        else:
            raise Exception(resp.text)

    def _current_user(self):
        return self.api_get("users/current/")

    def api_get(self, local_url, body=None):
        return self.api_request("get", local_url, body=body)

    def api_post(self, local_url, body=None):
        return self.api_request("post", local_url, body=body)

    def scrap(self):
        time_str = datetime.strftime(self.last_point, "%Y-%m-%d %H:%M:%S %f")
        messages_ans = self.api_get(f"messages/?receiver={self.USER_ID}&after={time_str}")
        messages = messages_ans["results"]
        if len(messages) == 0: return []
        self.last_point = datetime.strptime(messages[0]["created_dttm"], "%Y-%m-%d %H:%M:%S %f")
        return messages

    def send_msg(self, action, channel, msg, receiver):
        self.api_post("messages/", body=dict(action=action, channel=channel, body=msg, receiver=receiver))
