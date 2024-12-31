import mashumaro.codecs.yaml as yaml_codec
import subprocess
from .paragraph_rich import HelpFormatter
from . import config_loader, mqttclient, messages, mounts

daemon_help = """
Run a subscribing daemon that listens for messages and handles them.
"""

def xdg_open(path_or_url):
    command = ['xdg-open', path_or_url]
    subprocess.run(command)

# deriving from messages.HandleMessage ensures we get quick errors if we're not
# handling all the message types.
class DaemonHandleMessage(messages.HandleMessage):
    def handleXdgOpenPath(self, topic: str, message: messages.XdgOpenPath):
        local_path = mounts.find_local_path_from_remote(
            message.path,
            message.publisherHostnames
        )
        print(f"m: {message} lp: {local_path}")
        if local_path is None:
            return
        xdg_open(local_path)

def daemon_command(config: config_loader.Config, args):
    handler = DaemonHandleMessage()
    def prepare_client(client):
        def on_connect(client, userdata, flags, reason_code, properties):
            print(f"Connected with result code {reason_code}")
            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            client.subscribe("#")

        def on_message(client, userdata, msg):
            message = yaml_codec.decode(msg.payload, messages.Message)
            handler.handle(msg.topic, message)

        client.on_connect = on_connect
        client.on_message = on_message

    client = mqttclient.create_client(config, prepare_client)
    client.loop_forever()

def setup_args_parser(subparsers, config):
    path = subparsers.add_parser('daemon', help=daemon_help, formatter_class=HelpFormatter)
    path.set_defaults(func=daemon_command)

