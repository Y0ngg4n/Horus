from kubernetes import client, config

import favicon

icon_cache = {}


class Kube:
    ingress: set
    ingress_groups: dict
    custom_apps_ingress: set
    custom_apps_ingress_groups: dict
    app_config: dict

    def __init__(self):
        self.ingress = set([])
        self.ingress_groups = {}
        self.custom_apps_ingress = set([])
        self.custom_apps_ingress_groups = {}
        self.app_config = {}

    def get_config(self, app_config):
        self.app_config = app_config

    def get_ingress(self, app_config):
        # Configs can be set in Configuration class directly or using helper utility
        ingress_list = set([])
        config.load_incluster_config()
        v1 = client.NetworkingV1Api()
        if app_config["ingress"]["all"]:
            ret = v1.list_ingress_for_all_namespaces(watch=False)
            for i in ret.items:
                if i:
                    parsed_ingress = self.parse_ingress(i)
                    if parsed_ingress:
                        ingress_list.add(parsed_ingress)
        else:
            for ns in app_config['ingress']['namespaces']:
                ret = v1.list_namespaced_ingress(namespace=ns, watch=False)
                for i in ret["items"]:
                    if i:
                        parsed_ingress = self.parse_ingress(i)
                        if parsed_ingress:
                            ingress_list.add(parsed_ingress)
        self.ingress = set(ingress_list)

    def parse_ingress(self, item):
        first_rule = item.spec.rules[0]
        if first_rule:
            host = first_rule.host
            first_path = first_rule.http.paths[0]
            if first_path:
                if not self.app_config['ingress']['allEnabled']:
                    enabled = item.metadata.annotations.get('horus/enabled')
                    if not enabled:
                        return None
                if item.spec.tls[0] and host in item.spec.tls[0].hosts:
                    url = "https://" + host + first_path.path.rstrip("/")
                    ingress_service = IngressService(url=url, name="", description="",
                                                     uptime_kuma=-1,
                                                     icon_url=self.get_favicon(url), group="",
                                                     target_blank=False, sub_pages="")
                else:
                    url = "http://" + host + first_path.path.rstrip("/")
                    ingress_service = IngressService(url=url, name="", description="",
                                                     uptime_kuma=-1,
                                                     icon_url=self.get_favicon(url), group="",
                                                     target_blank=False, sub_pages="")

                ingress_service.group = item.metadata.namespace

                name = item.metadata.annotations.get('horus/name')
                group = item.metadata.annotations.get('horus/group')
                description = item.metadata.annotations.get('horus/description')
                uptime_kuma = item.metadata.annotations.get('horus/uptime-kuma')
                icon_url = item.metadata.annotations.get('horus/icon-url')
                url = item.metadata.annotations.get('horus/url')
                target_blank = item.metadata.annotations.get('horus/target-blank')
                sub_pages = item.metadata.annotations.get('horus/sub-pages')
                if name:
                    ingress_service.name = name
                else:
                    ingress_service.name = item.metadata.name
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

    def parse_custom_apps(self):
        if "customApps" not in self.app_config:
            return self.custom_apps_ingress_groups, set(self.get_sorted_ingress_list(self.custom_apps_ingress))
        apps = self.app_config["customApps"]
        if apps:
            for group in apps:
                custom_apps = set([])
                name = group['group']
                if name in self.custom_apps_ingress_groups:
                    custom_apps = set(self.custom_apps_ingress_groups[name])
                for app in group["apps"]:
                    url = app["url"]
                    icon = self.get_favicon(url)
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
                                                     description=description, uptime_kuma=uptime_kuma,
                                                     sub_pages=sub_pages)
                    custom_apps.add(ingress_service)
                    self.custom_apps_ingress.add(ingress_service)
                self.custom_apps_ingress_groups[name] = self.get_sorted_ingress_list(custom_apps)
        self.custom_apps_ingress = set(self.get_sorted_ingress_list(self.custom_apps_ingress))
        self.ingress = self.custom_apps_ingress.copy()
        self.ingress_groups = self.custom_apps_ingress_groups.copy()

    def update_ingress(self, ):
        print("Ingress: Updating ...")
        try:
            self.get_ingress(self.app_config)
            self.ingress.union(self.custom_apps_ingress)
            tmp_ingress_groups = self.custom_apps_ingress_groups.copy()
            print(self.ingress)
            for ing in self.ingress:
                if "excludeIngress" in self.app_config and ing.name in self.app_config["excludeIngress"]:
                    continue
                if ing.group in tmp_ingress_groups:
                    item_list = set(tmp_ingress_groups.get(ing.group))
                    item_list.add(ing)
                    tmp_ingress_groups[ing.group] = self.get_sorted_ingress_list(item_list)
                else:
                    tmp_ingress_groups[ing.group] = [ing, ]
            self.ingress_groups = tmp_ingress_groups
            del tmp_ingress_groups
        except Exception as e:
            print("Ingress: Could not update!")
            print(e)
        print("Ingress: Updated")

    @staticmethod
    def get_sorted_ingress_list(list):
        return sorted(list, key=lambda item: item.name)

    @staticmethod
    def get_favicon(url):
        try:
            if url not in icon_cache:
                icons = favicon.get(url)
                if icons[0] and icons[0].url:
                    icon_cache[url] = icons[0].url
                else:
                    icon_cache[url] = url.rstrip("/") + "/favicon.ico"
                return icon_cache[url]
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
