from kubernetes import client, config

import app


def get_ingress():
    app_config = app.load_config()
    # Configs can be set in Configuration class directly or using helper utility
    config.load_incluster_config()
    v1 = client.NetworkingV1Api()
    ingress_list = []
    if app_config["ingress"]["all"]:
        ret = v1.list_ingress_for_all_namespaces(watch=False)
        for i in ret.items:
            parsed_ingress = parse_ingress(i, app_config)
            if parsed_ingress:
                ingress_list.append(parsed_ingress)
    else:
        for ns in app_config['ingress']['namespaces']:
            ret = v1.list_namespaced_ingress(namespace=ns, watch=False)
            for i in ret.items:
                parsed_ingress = parse_ingress(i, app_config)
                if parsed_ingress:
                    ingress_list.append(parsed_ingress)
    return ingress_list


def parse_ingress(ingress, app_config):
    first_rule = ingress.spec.rules[0]
    if first_rule:
        host = first_rule.host
        first_path = first_rule.http.paths[0]
        if first_path:
            if ingress.spec.tls[0] and host in ingress.spec.tls[0].hosts:
                ingress_service = IngressService(url="https://" + host + first_path.path, name="", description="",
                                                 uptime_kuma=-1,
                                                 icon_url="https://" + host + first_path.path + "favicon.ico", group="")
            else:
                ingress_service = IngressService(url="http://" + host + first_path.path, name="", description="",
                                                 uptime_kuma=-1,
                                                 icon_url="http://" + host + first_path.path + "favicon.ico", group="")
            if not app_config['ingress']['allEnabled']:
                enabled = ingress.metadata.annotations.get('horus/enabled')
                print(ingress.metadata.annotations.get('horus/name') + " " + enabled)
                if not enabled:
                    return None

            ingress_service.group = ingress.metadata.namespace

            name = ingress.metadata.annotations.get('horus/name')
            group = ingress.metadata.annotations.get('horus/group')
            description = ingress.metadata.annotations.get('horus/description')
            uptime_kuma = ingress.metadata.annotations.get('horus/uptime-kuma')
            icon_url = ingress.metadata.annotations.get('horus/icon_url')
            if name:
                ingress_service.name = name
            else:
                ingress_service.name = ingress.metadata.name
            if description:
                ingress_service.description = description
            if uptime_kuma:
                ingress_service.uptime_kuma = int(uptime_kuma)
            if icon_url:
                ingress_service.iconUrl = int(icon_url)
            if group:
                ingress_service.group = group
            return ingress_service


class IngressService:
    def __init__(self, name: str, description: str, group: str, url: str, icon_url: str, uptime_kuma: int):
        self.name = name
        self.description = description
        self.url = url
        self.group = group
        self.icon_url = icon_url
        self.uptime_kuma = uptime_kuma
