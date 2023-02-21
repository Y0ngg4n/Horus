from kubernetes import client, config

import app
import favicon

icon_cache = {}


def get_ingress():
    app_config = app.load_config()
    # Configs can be set in Configuration class directly or using helper utility
    ingress_list = set([])
    config.load_incluster_config()
    v1 = client.NetworkingV1Api()
    if app_config["ingress"]["all"]:
        ret = v1.list_ingress_for_all_namespaces(watch=False)
        for i in ret.items:
            parsed_ingress = parse_ingress(i, app_config)
            if parsed_ingress:
                ingress_list.add(parsed_ingress)
    else:
        for ns in app_config['ingress']['namespaces']:
            ret = v1.list_namespaced_ingress(namespace=ns, watch=False)
            for i in ret.items:
                parsed_ingress = parse_ingress(i, app_config)
                if parsed_ingress:
                    ingress_list.add(parsed_ingress)
    return set(ingress_list)


def parse_ingress(ingress, app_config):
    first_rule = ingress.spec.rules[0]
    if first_rule:
        host = first_rule.host
        first_path = first_rule.http.paths[0]
        if first_path:
            if not app_config['ingress']['allEnabled']:
                enabled = ingress.metadata.annotations.get('horus/enabled')
                if not enabled:
                    return None
            if ingress.spec.tls[0] and host in ingress.spec.tls[0].hosts:
                url = "https://" + host + first_path.path.rstrip("/")
                ingress_service = IngressService(url=url, name="", description="",
                                                 uptime_kuma=-1,
                                                 icon_url=get_favicon(url), group="",
                                                 target_blank=False, sub_pages="")
            else:
                url = "http://" + host + first_path.path.rstrip("/")
                ingress_service = IngressService(url=url, name="", description="",
                                                 uptime_kuma=-1,
                                                 icon_url=get_favicon(url), group="",
                                                 target_blank=False, sub_pages="")

            ingress_service.group = ingress.metadata.namespace

            name = ingress.metadata.annotations.get('horus/name')
            group = ingress.metadata.annotations.get('horus/group')
            description = ingress.metadata.annotations.get('horus/description')
            uptime_kuma = ingress.metadata.annotations.get('horus/uptime-kuma')
            icon_url = ingress.metadata.annotations.get('horus/icon-url')
            url = ingress.metadata.annotations.get('horus/url')
            target_blank = ingress.metadata.annotations.get('horus/target-blank')
            sub_pages = ingress.metadata.annotations.get('horus/sub-pages')
            if name:
                ingress_service.name = name
            else:
                ingress_service.name = ingress.metadata.name
            if description:
                ingress_service.description = description
            if uptime_kuma:
                ingress_service.uptime_kuma = int(uptime_kuma)
            if icon_url:
                ingress_service.icon_url = icon_url
            if url:
                ingress_service.url = url.rstrip("/")
            if group:
                ingress_service.group = group
            if target_blank:
                ingress_service.target_blank = target_blank
            if sub_pages:
                ingress_service.sub_pages = sub_pages
            return ingress_service


def parse_custom_apps(app_config, ingress_groups, ingress_list):
    if "customApps" not in app_config.keys():
        return ingress_groups, set(getSortedIngressList(ingress_list))
    apps = app_config["customApps"]
    if apps:
        for group in apps:
            custom_apps = set([])
            name = group['group']
            if name in ingress_groups.keys():
                custom_apps = set(ingress_groups[name])
            for app in group["apps"]:
                url = app["url"]
                icon = get_favicon(url)
                if "icon" in app:
                    icon = app["icon"]
                target_blank = False
                if "targetBlank" in app:
                    target_blank = app["targetBlank"]
                description = ""
                if "description" in app:
                    description = app["description"]
                uptime_kuma = -1
                if "uptimeKuma" in app:
                    uptime_kuma = int(app["uptimeKuma"])
                sub_pages = ""
                if "subPages" in app:
                    sub_pages = app["subPages"]
                ingress_service = IngressService(name=app["name"], url=url, icon_url=icon,
                                                 target_blank=target_blank, group=name,
                                                 description=description, uptime_kuma=uptime_kuma, sub_pages=sub_pages)
                custom_apps.add(ingress_service)
                ingress_list.add(ingress_service)
            ingress_groups[name] = getSortedIngressList(custom_apps)
        return ingress_groups, set(getSortedIngressList(ingress_list))
    else:
        return ingress_groups, set(getSortedIngressList(ingress_list))


def getSortedIngressList(list):
    return sorted(list, key=lambda item: item.name)


def get_favicon(url):
    try:
        if url in icon_cache:
            return icon_cache[url]
        icons = favicon.get(url)
        favicon_hit = url.rstrip("/") + "/favicon.ico"
        if icons[0]:
            favicon_hit = icons[0].url
        icon_cache[url] = favicon_hit
        return favicon_hit
    except:
        return url.rstrip("/") + "/favicon.ico"


class IngressService:
    def __init__(self, name: str, description: str, group: str, url: str, icon_url: str, uptime_kuma: int,
                 target_blank: bool, sub_pages: str):
        self.name = name
        self.description = description
        self.url = url
        self.group = group
        self.icon_url = icon_url
        self.uptime_kuma = uptime_kuma
        self.target_blank = target_blank
        self.sub_pages = sub_pages
