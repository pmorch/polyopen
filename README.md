# **NOTE**: Work in progress.

## Polyopen

Send URls, notes, filenames between different clients.

An MQTT server is used as a router for publishers to request files, URLs, VS
Code sessions to be launched on subscribers or for publishers to send Markdown
notes from publisher to subscriber.

An open-source version of [Pushbullet](https://www.pushbullet.com/) plus support
for terminal apps.

## Project status

What is working is to launch a file, URL or VS Code session from one terminal on
one machine to cause a terminal on another machine to launch them.

Still missing:

* All browser and mobile implementations.
* Details of `publisherHostnames` / `subscriptions` / `destinationTopics` are
  not really elegant and likely to change.
  * Currently the subscriber daemon subscribes to topic `#` == *all*, so it
    doesn't matter what the publisher uses.

## Goals

The goal is to support these use cases:

1. From ssh terminal on `computerX`:
    1. Open `/home/user/work/path/file.ext` as ssh-mount
       `/mnt/remote/work/path.ext` on `computerY` using `xdg-open`.
    1. Open https://example.com in browser on `computerY`
    1. VS Code support:
        1. Open `/home/peter/work/path` as
          `vscode-remote://ssh-remote+computerX/home/peter/work/path`
        1. Open `/etc/some/file` as
           `vscode-remote://ssh-remote+computerX/etc/some/file` in the same
           window
1. From Android phone:
    1. Open https://example.com/page.html in browser on `computerY`.
    1. Send/receive "My text message" to browsers or phones
1. From browser on `computerY`:
    1. Open https://example.com/page.html on android phone
    1. Send/receive "My text message" to browsers or phones

## Design

### MQTT broker

A central MQTT broker is used to route messages between the different computers,
browsers and phones.

The publisher is indicated by the MQTT `clientId`. And the subscriber is
indicated by the MQTT topic, perhaps under some prefix.

### Messages

Messages are sent using JSON. The structure is:

TODO: Convert pseudo-code below to e.g. JSON Schema.

```
oneOf {
  xdg-open-path {
    publisherHostnames: list[string]
    path: string
  }
  vscode {
    publisherHostname: string
    isFile: boolean
    reuseWindow: boolean
    path: string
  }
  xdg-open-url {
    URL: string
  }
  markdown-message: string
}
```

#### `xdg-open-path`

`publisherHostnames` is a list of hostnames by which the publisher is expected
to be known by the subscriber and for which remote file systems are expected to
be mounted.

We investigate the current `fuse.sshfs` or NFS mount points for these host names
and derive the local path according to these mounts.

`path` is an absolute path to a file or dir.

So if we e.g. get:

```json
{
  "xdg-open-path": {
    "publisherHostnames": [ "kosh", "home" ],
    "path": "/home/peter/path/to/file.ext"
  }
}
```

And have a mount point such as:

```
kosh:/home/peter on /home/pmorch/mnt/tmp type fuse.sshfs
```

We know that `/home/peter/path/to/file.ext` on the publisher side means to call:

```shell
$ xdg-open /home/pmorch/mnt/tmp/path/to/file.ext
```

If multiple mount points can access the same file, which one will get used is
currently undefined.

For `xdg-open-path` to work, `fuse.sshfs` or NFS mount points need to already be
mounted when the message is received. Polyopen does not mount file systems for
you.

#### vscode

Here we'll be using VS Code's
[documented](https://code.visualstudio.com/docs/remote/troubleshooting#_connect-to-a-remote-host-from-the-terminal)
API for opening remote files and directories:

```shell
$ code --folder-uri vscode-remote://ssh-remote+remote_server/code/folder.with.dot
$ code --file-uri vscode-remote://ssh-remote+remote_server/code/fileWithoutExtension
```

So the remote server is expected to be known as the message's `publisherHostname`
because that is what will be used as `remote_server` in the `code` command.

If `reuseWindow` is true, the `--reuse-window` option will also be added the
`code` command.

#### xdg-open-url

Nothing magic here. Only ftp, http and https URLs are supported. (Patches
welcome)


We'll call:

```shell
$ xdg-open $url
```

#### `markdown-message`

Display the received message.

### Linux Terminal apps

Command line terminal apps can be used to publish messages to the MQTT broker
and to subscribe to them. They support all message types.

#### Configuration

Create `$HOME/.config/polyopen/config.yaml` with e.g.:

```
MQTT:
  host: mqtt.example.com
  port: 443
  # Having a local cert is not yet implemented. Patches welcome.
  certRequired: true
  auth:
    username: foo
    password: bar
  # Any topic will be ${topicPrefix}/${topic}
  topicPrefix: my-prefix
clientId: kosh-terminal
publisherHostnames:
  - kosh
  - home
subscriptions:
  - kosh-terminal
  - terminals
destinationTopics:
  # Specific destinations
  - kosh-browser
  - work-browser
  - work-terminal
  - samsung-phone
  - pixel7-phone
  # And groups
  - terminals
  - browsers
  - phones
```

#### Terminal publisher app

Here the `clientId` will be the `clientId` from the configuration with `-pub`
appended.

#### Terminal subscriber app

This will actually perform the actions, calling `xdg-open` and `code`.

Handling markdown messages, implies that the subscriber app stores the received
messages, which is probably a good idea anyway.

## Future enhancements

* Document autostart with `.desktop` file or `systemd` (with [`Requires=xdg-desktop-autostart.target`](https://unix.stackexchange.com/a/730170/8239)).
  * See/update [discussion](https://askubuntu.com/questions/1498075)
  * systemd has advantages:
    * Logging of stdout/stderr
    * Allow stop/start
    * Restart on crash/failure
* Subscriber Discovery: Currently the configuration requires the users to
  maintain a list of topics. That gets unwieldy when the number of clients
  grows. And in this application there is a one-to-one between
* Do we need the terminal subscriber to do anything else? Then perhaps we need
  asyncio instead of `client.loop_forever()`
* Ack using MQTT request/response.
  * [paho.mqtt.python](https://github.com/eclipse-paho/paho.mqtt.python) does
    not really document how to do this. [How to implement a request-response
    pattern with paho mqtt java? - Stack
    Overflow](https://stackoverflow.com/questions/62263089/how-to-implement-a-request-response-pattern-with-paho-mqtt-java)
    discusses how to do it with the paho java client.

## Links

* [mqttjs/MQTT.js: MQTT client the browser](https://github.com/mqttjs/MQTT.js)
* Web apps
  * [Use web apps - Android - Google Chrome Help][use-web-apps]
  * [Get started with PWAs - Microsoft Edge Developer documentation | Microsoft
    Learn][get-started-with-pwas]
  * [Receiving shared data with the Web Share Target API | Chrome for
    Developers][web-share-target]
  * [Web Share Test][web-share-test]

[use-web-apps]: https://support.google.com/chrome/answer/9658361?hl=en&co=GENIE.Platform%3DAndroid
[get-started-with-pwas]: https://learn.microsoft.com/en-us/microsoft-edge/progressive-web-apps-chromium/how-to/
[web-share-target]: https://developer.chrome.com/docs/capabilities/web-apis/web-share-target
[web-share-test]: https://w3c.github.io/web-share/demos/share.html

