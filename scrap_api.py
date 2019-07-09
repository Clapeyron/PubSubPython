import requests
from datetime import datetime
from dateutil.parser import parse as parse_dttm


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

    def scrap(self):
        time_str = str(self.last_point).split("+", 1)[0]
        messages_ans = self.api_get(f"messages/?receiver={self.USER_ID}&after={time_str}")
        messages = messages_ans["results"]
        if len(messages) == 0: return []
        self.last_point = parse_dttm(messages[-1]["created_dttm"], ignoretz=True)
        return messages
