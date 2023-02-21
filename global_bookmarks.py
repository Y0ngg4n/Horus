import kube


class GlobalBookMarks:
    global_bookmarks: dict

    def parse_global_bookmarks(self, config):
        if "globalBookmarks" not in config:
            return {}
        bm = config["globalBookmarks"]
        if bm:
            group_bookmarks = {}
            for group in bm:
                name = group['group']
                bookmarks = set([])
                for bookmark in group["bookmarks"]:
                    url = bookmark["url"]
                    icon_url = kube.Kube.get_favicon(url)
                    if "icon" in bookmark:
                        icon_url = bookmark["icon"]
                    target_blank = False
                    if "targetBlank" in bookmark:
                        target_blank = bookmark["targetBlank"]
                    sub_pages = ""
                    if "subPages" in bookmark:
                        sub_pages = bookmark["subPages"]
                    bookmarks.add(GlobalBookmark(name=bookmark["name"], url=url, icon_url=icon_url,
                                                 target_blank=target_blank, group=name, sub_pages=sub_pages))
                group_bookmarks[name] = bookmarks
            self.global_bookmarks = group_bookmarks
        else:
            self.global_bookmarks = {}

    @staticmethod
    def get_sorted_bookmarks_list(list):
        return sorted(list, key=lambda item: item.name)


class GlobalBookmark:
    def __init__(self, name: str, group: str, url: str, icon_url: str, target_blank: bool, sub_pages: str):
        self.name = name
        self.url = url
        self.group = group
        self.icon_url = icon_url
        self.target_blank = target_blank
        self.sub_pages = sub_pages
