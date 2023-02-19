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

ingress = set([])
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
                           sorted_ingress_groups_keys=sorted(ingress_groups.keys()),
                           ingress_groups=ingress_groups,
                           sorted_global_bookmarks_keys=sorted(global_bookmarks.keys()),
                           global_bookmarks=global_bookmarks,
                           uptime_kuma_status=uptime_kuma_status, backgroundColor=config["backgroundColor"],
                           primaryColor=config["primaryColor"], accentColor=config["accentColor"],
                           onlineColor=config["onlineColor"], offlineColor=config["offlineColor"])

def uptime_kuma():
    global api
    try:
        print("Getting uptime kuma")
        config = load_config()
        print(config['uptime-kuma']['url'])
        api = UptimeKumaApi(os.getenv("UPTIME_KUMA_URL") or config['uptime-kuma']['url'])
        login()
        print(api.info())
    except:
        print("Could not get Uptime Kuma")


def login():
    global api
    config = load_config()
    api.login(os.getenv("UPTIME_KUMA_USERNAME") or config['uptime-kuma']['username'],
              os.getenv("UPTIME_KUMA_PASSWORD") or config['uptime-kuma']['password'])


def get_uptime_kuma_status():
    return api.get_heartbeat()


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
    print("Ingress: Updating ...")
    ingress = kube.get_ingress()
    ingress_groups.clear()
    parse_config_items()
    for ing in ingress:
        if "excludeIngress" in config.keys() and ing.name in config["excludeIngress"]:
            continue
        if ing.group in ingress_groups.keys():
            item_list = set(ingress_groups.get(ing.group))
            item_list.add(ing)
            ingress_groups[ing.group] = kube.getSortedIngressList(item_list)
        else:
            ingress_groups[ing.group] = [ing, ]
    ingress_groups = ingress_groups
    print("Ingress: Updated")


def update_uptime_kuma():
    global ingress, uptime_kuma_status
    uptime_kuma_status.clear()
    login()
    print("Uptime Kuma: Update ...")
    try:
        status_list = get_uptime_kuma_status()
        for ing in ingress:
            if ing.uptime_kuma == -1:
                continue
            latest_timestamp = datetime.min
            latest_heartbeat = None
            monitorIdCount = 0
            for status in status_list:
                if int(status["id"]) == ing.uptime_kuma:
                    monitorIdCount += 1
                    timestamp = status["time"]
                    timestamp = datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S.%f")
                    if timestamp > latest_timestamp:
                        latest_timestamp = timestamp
                        latest_heartbeat = status
                    if latest_heartbeat:
                        print(ing.name + " " + str(latest_heartbeat["status"]))
                        uptime_kuma_status[ing] = latest_heartbeat["status"]
            print("Monitor Count for " + ing.name)
        print("Uptime Kuma: Updated")
    except Exception as e:
        print("Uptime Kuma: Could not update!")
        print(e)
        uptime_kuma_status = {}


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
    schedule.every(60).seconds.do(update_ingress)
    schedule.every(30).seconds.do(update_uptime_kuma)
    schedule.run_all()
    schedule_thread = threading.Thread(target=run_scheduler)
    schedule_thread.start()
    serve(app, host="0.0.0.0", port=8080)
