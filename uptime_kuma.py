from uptime_kuma_api import UptimeKumaApi
import os
import datetime
from datetime import datetime

api = None
url = ""
username = ""
password = ""


def get_config(config):
    global username, password, url
    if "uptime-kuma" in config and "username" in config["uptime-kuma"] and "password" in config["uptime-kuma"]:
        username = config['uptime-kuma']['username']
        password = config['uptime-kuma']['password']
    username = os.getenv("UPTIME_KUMA_USERNAME") or username
    password = os.getenv("UPTIME_KUMA_PASSWORD") or password
    if "uptime-kuma" in config and "url" in config["uptime-kuma"]:
        url = config['uptime-kuma']['url']
    url = os.getenv("UPTIME_KUMA_URL") or url


def uptime_kuma():
    global api
    try:
        print("Getting Uptime Kuma")
        api = UptimeKumaApi(url)
        print(api.info())
        return api
    except Exception as e:
        print("Could not get Uptime Kuma")
        print(e)


def update_uptime_kuma(ingress, uptime_kuma_status):
    print("Uptime Kuma: Update ...")
    try:
        tmp_uptime_kuma_status = {}
        status_list = get_uptime_kuma_status()
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
            uptime_kuma_status[ing] = tmp_uptime_kuma_status[ing]
        del tmp_uptime_kuma_status
        del status_list
        print("Uptime Kuma: Updated")
    except Exception as e:
        print("Uptime Kuma: Could not update!")
        print(e)


def get_uptime_kuma_status():
    return api.get_important_heartbeats()


def login():
    if not api:
        uptime_kuma()
    api.login(username, password)
