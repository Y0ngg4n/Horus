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
    return get_index()


@app.route("/health")
def health():
    return "Ok"


@app.route("/<subpage>")
def subpages(subpage):
    return get_index(subpage)


def get_index(subpage=""):
    global ingress, ingress_groups, global_bookmarks
    local_ingress = ingress
    local_ingress_groups = ingress_groups
    local_global_bookmarks = global_bookmarks
    tmp_ingress = set([])
    for i in local_ingress:
        if (not i.sub_pages and not subpage) or (subpage in get_sub_pages(i.sub_pages)) or (
                not subpage and "default" in get_sub_pages(i.sub_pages)):
            tmp_ingress.add(i)
    local_ingress = kube.getSortedIngressList(tmp_ingress)
    tmp_ingress_group = {}
    for group in local_ingress_groups:
        tmp_ingress = set([])
        for i in local_ingress_groups[group]:
            if (not i.sub_pages and not subpage) or (subpage in get_sub_pages(i.sub_pages)) or (
                    not subpage and "default" in get_sub_pages(i.sub_pages)):
                tmp_ingress.add(i)
        if len(tmp_ingress) > 0:
            tmp_ingress_group[group] = kube.getSortedIngressList(tmp_ingress)
    local_ingress_groups = tmp_ingress_group
    local_sorted_ingress_groups_keys = sorted(local_ingress_groups.keys())
    tmp_book_marks_group = {}
    for group in local_global_bookmarks:
        tmp_book_marks = set([])
        for bookmark in local_global_bookmarks[group]:
            if (not bookmark.sub_pages and not subpage) or (subpage in get_sub_pages(bookmark.sub_pages)) or (
                    not subpage and "default" in get_sub_pages(bookmark.sub_pages)):
                tmp_book_marks.add(bookmark)
        if len(tmp_book_marks) > 0:
            tmp_book_marks_group[group] = gb.getSortedBookmarksList(tmp_book_marks)
    local_global_bookmarks = tmp_book_marks_group
    local_sorted_global_bookmarks_keys = sorted(local_global_bookmarks.keys())

    config = load_config()

    greeting = "Welcome, Searcher!"
    if "greeting" in config:
        greeting = config["greeting"]
    title = "Horus"
    if "title" in config:
        title = config["title"]
    background_color = "#232530"
    if "backgroundColor" in config:
        background_color = config["backgroundColor"]
    primary_color = "#232530"
    if "primaryColor" in config:
        primary_color = config["primaryColor"]
    accent_color = "#232530"
    if "accentColor" in config:
        accent_color = config["accentColor"]
    online_color = "#232530"
    if "onlineColor" in config:
        online_color = config["onlineColor"]
    offline_color = "#232530"
    if "offlineColor" in config:
        offline_color = config["offlineColor"]
    show_greeting = True
    if "showGreeting" in config:
        show_greeting = config["showGreeting"]
    show_search = True
    if "showSearch" in config:
        show_greeting = config["showSearch"]
    show_app_groups = True
    if "showAppGroups" in config:
        show_app_groups = config["showAppGroups"]
    show_app_urls = True
    if "showAppUrls" in config:
        show_app_urls = config["showAppUrls"]
    show_app_description = False
    if "showAppDescription" in config:
        show_app_description = config["showAppDescription"]
    show_app_status = True
    if "showAppStatus" in config:
        show_app_status = config["showAppStatus"]
    show_global_bookmarks = False
    if "showGlobalBookmarks" in config:
        show_global_bookmarks = config["showGlobalBookmarks"]
    always_target_blank = False
    if "alwaysTargetBlank" in config:
        always_target_blank = config["alwaysTargetBlank"]
    return render_template("index.html", title=title, showGreeting=show_greeting,
                           showSearch=show_search,
                           showAppGroups=show_app_groups,
                           showAppUrls=show_app_urls, showAppDescription=show_app_description,
                           showAppStatus=show_app_status,
                           showGlobalBookmarks=show_global_bookmarks,
                           alwaysTargetBlank=always_target_blank,
                           greeting=greeting, ingress=local_ingress,
                           sorted_ingress_groups_keys=local_sorted_ingress_groups_keys,
                           ingress_groups=local_ingress_groups,
                           sorted_global_bookmarks_keys=local_sorted_global_bookmarks_keys,
                           global_bookmarks=local_global_bookmarks,
                           uptime_kuma_status=uptime_kuma_status, backgroundColor=background_color,
                           primaryColor=primary_color, accentColor=accent_color,
                           onlineColor=online_color, offlineColor=offline_color)


def get_sub_pages(sub_pages):
    if sub_pages:
        return sub_pages.split(",")
    else:
        return []


def uptime_kuma():
    global api
    try:
        print("Getting uptime kuma")
        config = load_config()
        url = ""
        if "uptime-kuma" in config and "url" in config["uptime-kuma"]:
            url = config['uptime-kuma']['url']
        api = UptimeKumaApi(os.getenv("UPTIME_KUMA_URL") or url)
        print(api.info())
    except Exception as e:
        print("Could not get Uptime Kuma")
        print(e)


def login():
    global api
    config = load_config()
    if not api:
        uptime_kuma()
    username = ""
    password = ""
    if "uptime-kuma" in config and "username" in config["uptime-kuma"] and "password" in config["uptime-kuma"]:
        username = config['uptime-kuma']['username']
        password = config['uptime-kuma']['password']
    api.login(os.getenv("UPTIME_KUMA_USERNAME") or username,
              os.getenv("UPTIME_KUMA_PASSWORD") or password)


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
    print("Ingress: Updating ...")
    try:
        ingress = kube.get_ingress()
        tmp_ingress_groups = {}
        parse_config_items()
        for ing in ingress:
            if "excludeIngress" in config.keys() and ing.name in config["excludeIngress"]:
                continue
            if ing.group in tmp_ingress_groups.keys():
                item_list = set(tmp_ingress_groups.get(ing.group))
                item_list.add(ing)
                tmp_ingress_groups[ing.group] = kube.getSortedIngressList(item_list)
            else:
                tmp_ingress_groups[ing.group] = [ing, ]
        ingress_groups = tmp_ingress_groups
    except Exception as e:
        print("Ingress: Could not update!")
        print(e)
    print("Ingress: Updated")


def update_uptime_kuma():
    global ingress, uptime_kuma_status
    print("Uptime Kuma: Update ...")
    try:
        login()
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
        print("Uptime Kuma: Updated")
    except Exception as e:
        print("Uptime Kuma: Could not update!")
        print(e)


def uptime_kuma_polling(uptime_kuma_poll_seconds):
    while True:
        update_uptime_kuma()
        time.sleep(uptime_kuma_poll_seconds)


def ingress_polling(ingress_poll_seconds):
    while True:
        update_ingress()
        time.sleep(ingress_poll_seconds)


def parse_config_items():
    global ingress, ingress_groups, global_bookmarks
    global_bookmarks = gb.parse_global_bookmarks(load_config())
    ingress_groups, ingress = kube.parse_custom_apps(load_config(), ingress_groups, set(ingress))
    config = load_config()
    uptime_kuma_poll_seconds = 30
    ingress_poll_seconds = 60
    if "uptimeKumaPollSeconds" in config:
        uptime_kuma_poll_seconds = int(config["uptimeKumaPollSeconds"])
    if "ingressPollSeconds" in config:
        ingress_poll_seconds = int(config["ingressPollSeconds"])
    uptime_kuma_disabled = False
    ingress_disabled = False
    if "uptime-kuma" in config and "disabled" in config["uptime-kuma"] and config["uptime-kuma"]["disabled"]:
        uptime_kuma_disabled = True
    if "ingress" in config and "disabled" in config["ingress"] and config["ingress"]["disabled"]:
        ingress_disabled = True
    return uptime_kuma_poll_seconds, ingress_poll_seconds, uptime_kuma_disabled, ingress_disabled


if __name__ == "__main__":
    ukps, ips, ukd, id = parse_config_items()
    if not ukd:
        uptime_kuma()
        login()
        uptime_kuma_thread = threading.Thread(target=uptime_kuma_polling, args=(ukps,))
        uptime_kuma_thread.start()
    if not id:
        ingress_thread = threading.Thread(target=ingress_polling, args=(ips,))
        ingress_thread.start()
    serve(app, host="0.0.0.0", port=8080)
