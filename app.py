import schedule
from flask import Flask, render_template, jsonify
from flask_assets import Bundle, Environment
from uptime_kuma_api import UptimeKumaApi
from dotenv import load_dotenv
import os
import yaml
import kube
import threading
import time
from datetime import datetime
import global_bookmarks as gb
from waitress import serve

load_dotenv()

app: Flask = Flask(__name__)

assets = Environment(app)
css = Bundle("src/main.css", output="dist/main.css")

assets.register("css", css)
css.build()

ingress = []
ingress_groups = {}
uptime_kuma_status = {}
global_bookmarks = {}
api = None

@app.route("/")
def homepage():
    config = load_config()
    return render_template("index.html", title=config["title"], showGreeting=config["showGreeting"],
                           showSearch=config["showSearch"],
                           showAppGroups=config["showAppGroups"],
                           showAppUrls=config["showAppUrls"], showAppStatus=config["showAppStatus"],
                           showGlobalBookmarks=config["showGlobalBookmarks"],
                           alwaysTargetBlank=config["alwaysTargetBlank"],
                           greeting=config["greeting"], ingress=ingress,
                           ingress_groups=ingress_groups,
                           global_bookmarks=global_bookmarks,
                           uptime_kuma_status=uptime_kuma_status, backgroundColor=config["backgroundColor"],
                           primaryColor=config["primaryColor"], accentColor=config["accentColor"],
                           onlineColor=config["onlineColor"], offlineColor=config["offlineColor"])

def uptime_kuma():
    global api
    print("Getting uptime kuma")
    config = load_config()
    print(config['uptime-kuma']['url'])
    api = UptimeKumaApi(os.getenv("UPTIME_KUMA_URL") or config['uptime-kuma']['url'])
    api.login(os.getenv("UPTIME_KUMA_USERNAME") or config['uptime-kuma']['username'],
              os.getenv("UPTIME_KUMA_PASSWORD") or config['uptime-kuma']['password'])
    print(api.info())


def get_uptime_kuma_status():
    return api.get_important_heartbeats()


def load_config():
    with open("config/config.yaml", "r") as stream:
        app.logger.info("Loading config ...")
        try:
            return yaml.safe_load(stream)
        except yaml.YAMLError as exc:
            print(exc)
            return None


def update_ingress():
    global ingress, ingress_groups
    config = load_config()
    print("Updating Ingress")
    ingress = kube.get_ingress()
    ingress_groups.clear()
    for ing in ingress:
        if "excludeIngress" in config.keys() and ing.name in config["excludeIngress"]:
            continue
        if ing.group in ingress_groups.keys():
            item_list = ingress_groups[ing.group]
            item_list.append(ing)
            ingress_groups[ing.group] = item_list
        else:
            ingress_groups[ing.group] = [ing, ]


def update_uptime_kuma():
    global ingress
    print("Update Uptime Kuma")
    uptime_kuma_status.clear()
    status_list = get_uptime_kuma_status()
    for ing in ingress:
        if ing.uptime_kuma != -1:
            for status in status_list:
                if int(status["id"]) == ing.uptime_kuma:
                    latest_timestamp = datetime.min
                    latest_heartbeat = None
                    for heartbeat in status["data"]:
                        timestamp = heartbeat["time"]
                        timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
                        if timestamp > latest_timestamp:
                            latest_timestamp = timestamp
                            latest_heartbeat = heartbeat
                    if latest_heartbeat:
                        uptime_kuma_status[ing] = latest_heartbeat["status"]
                    break


def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)


def parse_config_items():
    global ingress, ingress_groups, global_bookmarks
    global_bookmarks = gb.parse_global_bookmarks(load_config())
    ingress_groups, ingress = kube.parse_custom_apps(load_config(), ingress_groups, ingress)


if __name__ == "__main__":
    parse_config_items()
    uptime_kuma()
    update_ingress()
    update_uptime_kuma()
    schedule.every(60).seconds.do(update_ingress)
    schedule.every(60).seconds.do(update_uptime_kuma)
    schedule_thread = threading.Thread(target=run_scheduler)
    schedule_thread.start()
    serve(app, host="0.0.0.0", port=8080)
