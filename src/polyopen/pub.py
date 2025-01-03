import os
from pathlib import Path

import mashumaro.codecs.yaml as yaml_codec
from rich.console import Console
from rich.markdown import Markdown

from . import config_loader, messages, mqttclient, valid_url
from .paragraph_rich import HelpFormatter

description = """
# For path, the path must exist already
polyopen path /path/to/file
polyopen path --dest work-terminal /path/to/file

polyopen url --dest remote-browser https://www.google.com
polyopen url --dest work-terminal https://www.google.com

# For vscode, the path must exist already
polyopen vscode /path/to/folder
polyopen vscode -r /path/to/file

polyopen note note.md
# polyopen uses stdin if no arg
echo foobar | polyopen note
"""


path_help = """
Open file or directory on remote machine using `xdg-open`.
"""

url_help = """
Open URL in remote browser
"""

code_help = """
Open local file or folder in vscode on subscriber
"""

dest_help = """
The destination
"""

list_help = """
List destinations
"""

reuse_help = """
Force to open a file or folder in an already opened window. (passed to vscode)
"""


def setup_args_parser(subparsers, config):
    default_destination = config.destinations[0]

    path = subparsers.add_parser("path", help=path_help, formatter_class=HelpFormatter)
    path.add_argument("--dest", "-d", help=dest_help, default=default_destination)
    path.add_argument("--list", "-l", action="store_true", help=list_help)
    path.add_argument("path")
    path.set_defaults(func=path_command)

    url = subparsers.add_parser("url", help=path_help, formatter_class=HelpFormatter)
    url.add_argument("--dest", "-d", help=dest_help, default=default_destination)
    url.add_argument("--list", "-l", action="store_true", help=list_help)
    url.add_argument("url")
    url.set_defaults(func=url_command)

    code = subparsers.add_parser("code", help=code_help, formatter_class=HelpFormatter)
    code.add_argument("--dest", "-d", help=dest_help, default=default_destination)
    code.add_argument("--list", "-l", action="store_true", help=list_help)
    code.add_argument("--reuse-window", "-r", action="store_true", help=reuse_help)
    code.add_argument("path")
    code.set_defaults(func=code_command)


def list_destinations(config: config_loader.Config, args):
    lines = ["## Destinations"]
    for i, dest in enumerate(config.destinations):
        if i == 0:
            dest += " *(default)*"
        lines.append(f"* {dest}")
    markdown = "\n".join(lines)
    console = Console()
    console.print(Markdown(markdown))


def canonical_absolute_path(path: str):
    """
    Return an absolute path without e.g. '..' segments.

    patlib.Path.resolve() resolves symlinks (which we don't want)

    pathlib.Path.absolute() makes a path absolute but keeps any '..' segments (which we don't want)
    """
    if not Path(path).exists():
        raise FileNotFoundError(f"{path} doesn't exist")
    return Path(os.path.abspath(path))


def publish_path(config: config_loader.Config, args):
    path = canonical_absolute_path(args.path)
    if not path.exists():
        raise FileNotFoundError(f"{args.path} does not exist")

    xdgOpenPath = messages.XdgOpenPath(
        path=str(path), publisherHostnames=config.publisherHostnames
    )
    message = messages.XdgOpenPathWithField(xdgOpenPath)
    publish_message(message, messages.XdgOpenPathWithField, args.dest)


def path_command(config: config_loader.Config, args):
    if args.list:
        list_destinations(config, args)
    else:
        publish_path(config, args)


def url_command(config: config_loader.Config, args):
    if args.list:
        list_destinations(config, args)
    else:
        url = args.url
        if not valid_url.is_valid_url(url):
            raise ValueError(f"{url} is not a valid URL")

        xdgOpenURL = messages.XdgOpenURL(URL=url)
        message = messages.XdgOpenURLWithField(xdgOpenURL)
        publish_message(message, messages.XdgOpenURLWithField, args.dest)


def code_command(config: config_loader.Config, args):
    if args.list:
        list_destinations(config, args)
    else:
        path = canonical_absolute_path(args.path)
        vscode = messages.VSCode(
            path=str(path),
            isFile=path.is_file(),
            publisherHostname=config.publisherHostnames[0],
            reuseWindow=args.reuse_window,
        )
        message = messages.VSCodeWithField(vscode)
        publish_message(message, messages.VSCodeWithField, args.dest)


def publish_message(message, message_type, dest):
    message_yaml = yaml_codec.encode(message, message_type)

    config = config_loader.load()

    config.clientId += "-pub"

    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")

    def on_connect_fail(client, error):
        print("on_connect_fail")

    def prepare_client(client):
        # client.on_connect = on_connect
        # client.on_connect_fail = on_connect_fail
        pass

    client = mqttclient.create_client(config, prepare_client)

    client.loop_start()

    msg_info = client.publish(dest, message_yaml, qos=1)
    msg_info.wait_for_publish()

    client.disconnect()
    client.loop_stop()
