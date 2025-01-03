import subprocess

import mashumaro.codecs.yaml as yaml_codec

from . import config_loader, messages, mounts, mqttclient, valid_url
from .paragraph_rich import HelpFormatter

daemon_help = """
Run a subscribing daemon that listens for messages and handles them.
"""

debug_help = """
Don't actually perform any actions, just print out the received messages.
"""


def xdg_open(path_or_url):
    command = ["xdg-open", path_or_url]
    subprocess.run(command)


def vscode_open(message: messages.VSCode):
    type_flag = "--file-uri" if message.isFile else "--folder-uri"
    remote = f"vscode-remote://ssh-remote+{message.publisherHostname}{message.path}"
    subprocess.run(["code", type_flag, remote])


# deriving from messages.HandleMessage ensures we get quick errors if we're not
# handling all the message types.
class DaemonHandleMessage(messages.HandleMessage):
    def handleXdgOpenPath(self, topic: str, message: messages.XdgOpenPath):
        local_path = mounts.find_local_path_from_remote(
            message.path, message.publisherHostnames
        )
        print(f"m: {message} lp: {local_path}")
        if local_path is None:
            return
        xdg_open(local_path)

    def handleXdgOpenURL(self, topic: str, message: messages.XdgOpenURL):
        url = message.URL
        if not valid_url.is_valid_url(url):
            raise ValueError(f"{url} is not a valid URL")
        xdg_open(url)

    def handleVSCode(self, topic: str, message: messages.VSCode):
        vscode_open(message)


def daemon_command(config: config_loader.Config, args):
    handler = DaemonHandleMessage()

    def prepare_client(client):
        def on_connect(client, userdata, flags, reason_code, properties):
            print(f"Connected with result code {reason_code}")
            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            client.subscribe("#")

        def on_message(client, userdata, msg):
            if args.debug:
                print(f"Topic: {msg.topic}")
                print(f"Payload: {msg.payload.decode('utf-8')}")
                return
            message = yaml_codec.decode(msg.payload, messages.Message)
            handler.handle(msg.topic, message)

        client.on_connect = on_connect
        client.on_message = on_message

    client = mqttclient.create_client(config, prepare_client)
    client.loop_forever()


def setup_args_parser(subparsers, config):
    path = subparsers.add_parser(
        "daemon", help=daemon_help, formatter_class=HelpFormatter
    )
    path.add_argument("--debug", "-d", action="store_true", help=debug_help)
    path.set_defaults(func=daemon_command)
