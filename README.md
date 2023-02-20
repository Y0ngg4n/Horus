# Horus

Horus is a [Hajimari](https://github.com/toboshii/hajimari) similar startpage designed to be the entrypoint for your
self-hosted Kubernetes cluster. Thanks to Hajimari for the great inspiration!

## Features

- Dynamically list apps discovered from Kubernetes ingresses
- Display replica status for ingress endpoints
- Support for non-Kubernetes apps via custom apps config
- Customizable list of bookmarks
- Selectable themes and custom theme support
- Automatic light/dark mode
- Add subpages so you show applications only on specific paths

## Usage

### Ingresses

Horus looks for specific annotations on ingresses.

> Add the following annotations to your ingresses in order for it to be discovered by Horus:

| Annotation           | Description                                                                                                                                                                                                                           | Required |
|----------------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| `horus/enabled`      | Add this with value `true` to the ingress of the app you want to show                                                                                                                                                                 | `true`   |
| `horus/name`         | A custom name for your application. Use if you don't want to use the name of the ingress                                                                                                                                              | `false`  |
| `horus/group`        | A custom group name. Use if you want the application to show in a different group than the namespace it is running in                                                                                                                 | `false`  |
| `horus/description`  | A short description of the app                                                                                                                                                                                                        | `false`  |
| `horus/uptime-kuma`  | Your App ID in Uptime Kuma. If not provided it will disable showing the status.                                                                                                                                                       | `false`  |
| `horus/icon-url`     | Icon URL, if not provided Favicon is used (if online it will show an offline icon)                                                                                                                                                    | `false`  |
| `horus/url`          | A URL for the app (This will override the ingress URL). It MUST begin with a scheme i.e., `http://` or `https://`                                                                                                                     | `false`  |
| `horus/target-blank` | Determines if links should open in new tabs/windows                                                                                                                                                                                   | `false`  |
| `horus/sub-pages`    | A comma-seperated list of subPages. This is helpful to show applications only on subPages. E.g. if you set sub-pages to "foo,bar", this app will only gets displayed if you go on https://example.com/foo and https://example.com/bar | `false`  |

### Config

Hajimari supports the following configuration options that can be modified by either ConfigMap or `values.yaml` if you
are using Helm

|         Field         |                          Description                          |       Default        | Type                                          |
|:---------------------:|:-------------------------------------------------------------:|:--------------------:|-----------------------------------------------|
|       greeting        |                     Your Greeting String                      | "Welcome, Searcher!" | string                                        |
|         title         |           Browser title for this Hajimari instance            |       "Horus"        | string                                        |
|    backgroundColor    |                Hex Color to use as background                 |      "#232530"       | string                                        |
|     primaryColor      |               Hex Color to use as primary color               |      "#232530"       | string                                        |
|      accentColor      |               Hex Color to use as accent color                |      "#232530"       | string                                        |
|      onlineColor      |           Hex Color to use as offline status color            |      "#232530"       | string                                        |
|     offlineColor      |            Hex Color to use as online status color            |      "#232530"       | string                                        |
|     showGreeting      |                  Toggle showing the greeting                  |         true         | bool                                          |
|      showSearch       |                   Toggle showing the search                   |         true         | bool                                          |
|     showAppGroups     |          Toggle grouping apps by group (namespaces)           |         true         | bool                                          |
|      showAppUrls      |                  Toggle displaying app URLs                   |         true         | bool                                          |
|  showAppDescription   |                Toggle showing app description                 |        false         | bool                                          |
|     showAppStatus     |             Toggle showing app Uptime Kuma status             |         true         | bool                                          |
|  showGlobalBookmarks  |     Toggle showing global bookmarks on custom startpages      |        false         | bool                                          |
|   alwaysTargetBlank   | Set to true to open apps/bookmarks in a new window by default |        false         | bool                                          |
| uptimeKumaPollSeconds |             Seconds schedule to poll Uptime Kuma              |          30          | int                                           |
|  ingressPollSeconds   |               Seconds schedule to poll Ingress                |          60          | int                                           |
|    excludeIngress     |              A list on ingress names to exclude               |          []          | string[]                                      |
|      customApps       |      A list of custom apps to add to the discovered apps      |          []          | \[\][AppGroup](#appgroup)                     |
|    globalBookmarks    |               A list of bookmark groups to add                |          []          | \[\][BookmarkGroup](#bookmarkgroup)           |
|        ingress        |                Settings for Ingress selection                 |          []          | \[\][IngressSettings](#ingresssettings)       |
|      uptime-kuma      |                   Settings for Uptime Kuma                    |          []          | \[\][UptimeKumaSettings](#uptimekumasettings) |

#### IngressSettings

It is a selector for selecting namespaces either selecting all namespaces or a list of namespaces

|   Field    |                                           Description                                           | Default | Type     |
|:----------:|:-----------------------------------------------------------------------------------------------:|:-------:|----------|
|    any     |  Boolean describing whether all namespaces are selected in contrast to a list restricting them  |  true   | bool     |
| anyEnabled | Boolean describing whether all ingress are enabled and showed (only if subPages is not defined) |  true   | bool     |
| namespaces |                                     List of namespace names                                     |  null   | []string |

#### UptimeKumaSettings

This are the Setting for connection with Uptime Kuma.

|  Field   |             Description              | Default | Type   |
|:--------:|:------------------------------------:|:-------:|--------|
|   url    | The URL of your Uptime Kuma instance |   ""    | string |
| username |       The Uptime Kuma username       |   ""    | string |
| password |       The Uptime Kuma password       |   ""    | string |

#### AppGroup

If you want to add any apps that are not exposed through ingresses or are external to the cluster, you can use the
custom apps feature. You can pass a list of custom apps inside the config.

| Field | Description                   | Type            |
|-------|-------------------------------|-----------------|
| group | Name of the group (namespace) | String          |
| apps  | A list of custom apps         | \[\][App](#app) |

##### App

Custom apps can be added by configuring a list of apps under an app group.

| Field       | Description                                                                                                                                                                                                                           | Type   |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|
| name        | Name of the custom app (Required)                                                                                                                                                                                                     | String |
| icon        | Icon name or URL for the custom app                                                                                                                                                                                                   | String |
| url         | URL of the custom app                                                                                                                                                                                                                 | String |
| description | Short description of the custom app                                                                                                                                                                                                   | String |
| targetBlank | Open app in a new window/tab                                                                                                                                                                                                          | Bool   |
| uptimeKuma  | The Uptime Kuma ID                                                                                                                                                                                                                    | String |
| subPages    | A comma-seperated list of subPages. This is helpful to show applications only on subPages. E.g. if you set sub-pages to "foo,bar", this app will only gets displayed if you go on https://example.com/foo and https://example.com/bar | String |

#### BookmarkGroup

Bookmark groups can be added by creating a list of groups and associated bookmarks.

| Field     | Description                | Type                      |
|-----------|----------------------------|---------------------------|
| group     | Name of the bookmark group | String                    |
| bookmarks | Array of bookmarks         | \[\][Bookmark](#bookmark) |

Bookmarks can be added by configuring a list of bookmarks under a group.

##### Bookmark

| Field       | Description                                                                                                                                                                                                                           | Type   |
|-------------|---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|--------|
| name        | Name of the bookmark (Required)                                                                                                                                                                                                       | String |
| icon        | Icon name or URL for the bookmark                                                                                                                                                                                                     | String |
| url         | URL of the bookmark (Required)                                                                                                                                                                                                        | String |
| targetBlank | Open bookmark in a new window/tab                                                                                                                                                                                                     | Bool   |
| subPages    | A comma-seperated list of subPages. This is helpful to show applications only on subPages. E.g. if you set sub-pages to "foo,bar", this app will only gets displayed if you go on https://example.com/foo and https://example.com/bar | String |

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## About

### Why Horus?

I wanted to choose a name that starts with an H to credit Hajimari´s work.

## Thank you / dependencies

- [Hajimari](https://github.com/toboshii/hajimari) For the great inspiration and your Readme

## License

[Apache-2.0](https://choosealicense.com/licenses/apache-2.0/)