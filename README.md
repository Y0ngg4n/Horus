# Horus

Horus is a [Hajimari](https://github.com/toboshii/hajimari) similar startpage designed to be the entrypoint for your self-hosted Kubernetes cluster.

## Features
- Dynamically list apps discovered from Kubernetes ingresses
- Display replica status for ingress endpoints
- Support for non-Kubernetes apps via custom apps config
- Customizable list of bookmarks
- Selectable themes and custom theme support
- Automatic light/dark mode
- Multiple instance support

### Ingresses

Hajimari looks for specific annotations on ingresses.

- Add the following annotations to your ingresses in order for it to be discovered by Hajimari:

| Annotation           | Description                                                                                                                                          | Required |
|----------------------|------------------------------------------------------------------------------------------------------------------------------------------------------|----------|
| `horus/enabled`      | Add this with value `true` to the ingress of the app you want to show                                                                                | `true`   |
| `horus/icon-url`     | Icon URL, if not provided Favicon is used                                                                                                            | `false`  |
| `horus/name`         | A custom name for your application. Use if you don't want to use the name of the ingress                                                             | `false`  |
| `horus/group`        | A custom group name. Use if you want the application to show in a different group than the namespace it is running in                                | `false`  |
| `horus/url`          | A URL for the Hajimari app (This will override the ingress URL). It MUST begin with a scheme i.e., `http://` or `https://`                           | `false`  |
| `horus/target-blank` | Determines if links should open in new tabs/windows                                                                                                  | `false`  |
| `horus/description`  | A short description of the Hajimari app                                                                                                              | `false`  |
