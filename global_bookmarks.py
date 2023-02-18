def parse_global_bookmarks(config):
    bm = config["globalBookmarks"]
    if bm:
        group_bookmarks = {}
        for group in bm:
            name = group['group']
            bookmarks = []
            for bookmark in group["bookmarks"]:
                bookmarks.append(GlobalBookmark(name=bookmark["name"], url=bookmark["url"], icon_url=bookmark["icon"],
                                                target_blank=bookmark["targetBlank"], group=name))
            group_bookmarks[name] = bookmarks
        return group_bookmarks
    else:
        return {}


class GlobalBookmark:
    def __init__(self, name: str, group: str, url: str, icon_url: str, target_blank: bool):
        self.name = name
        self.url = url
        self.group = group
        self.icon_url = icon_url
        self.target_blank = target_blank
