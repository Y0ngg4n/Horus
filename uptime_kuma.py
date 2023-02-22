from uptime_kuma_api import UptimeKumaApi
import os
import datetime
from datetime import datetime


class UptimeKuma:
    api: UptimeKumaApi
    url: str
    username: str
    password: str
    uptime_kuma_status: dict

    def __init__(self):
        self.url = ""
        self.username = ""
        self.password = ""
        self.uptime_kuma_status = {}

    def get_config(self, config):
        if "uptime-kuma" in config and "username" in config["uptime-kuma"] and "password" in config["uptime-kuma"]:
            self.username = config['uptime-kuma']['username']
            self.password = config['uptime-kuma']['password']
        self.username = os.getenv("UPTIME_KUMA_USERNAME") or self.username
        self.password = os.getenv("UPTIME_KUMA_PASSWORD") or self.password
        if "uptime-kuma" in config and "url" in config["uptime-kuma"]:
            self.url = config['uptime-kuma']['url']
        self.url = os.getenv("UPTIME_KUMA_URL") or self.url
        print(self.url)

    def connect(self):
        try:
            print("Getting Uptime Kuma")
            self.api = UptimeKumaApi(self.url)
            print(self.api.info())
            return self.api
        except Exception as e:
            print("Could not get Uptime Kuma")
            print(e)

    def login(self):
        if not self.api:
            self.connect()
        self.api.login(self.username, self.password)

    def update(self, ingress):
        print("Uptime Kuma: Update ...")
        try:
            tmp_uptime_kuma_status = {}
            status_list = self.get_current_status()
            for ing in ingress:
                if ing.uptime_kuma == -1:
                    continue
                latest_timestamp = datetime.min
                latest_heartbeat = None
                for status in status_list:
                    for data in status["data"]:
                        if int(data["monitorID"]) == ing.uptime_kuma:
                            timestamp = data["time"]
                            timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
                            if timestamp > latest_timestamp:
                                latest_timestamp = timestamp
                                latest_heartbeat = data
                if latest_heartbeat:
                    # print(ing.name + " " + str(latest_heartbeat["status"]))
                    tmp_uptime_kuma_status[ing] = latest_heartbeat["status"]
            for ing in tmp_uptime_kuma_status.keys():
                self.uptime_kuma_status[ing] = tmp_uptime_kuma_status[ing]
            del tmp_uptime_kuma_status
            del status_list
            print("Uptime Kuma: Updated")
        except Exception as e:
            print("Uptime Kuma: Could not update!")
            print(e)

    def get_current_status(self):
        return self.api.get_important_heartbeats()