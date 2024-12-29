import paho.mqtt.client as mqtt
import ssl
import yaml
from pathlib import Path
from rich import print
from munch import Munch


def create_client(config, prepare_client):
    pass

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        transport=config['MQTT']['transport'],
        client_id=config.clientId
    )
    if (config.MQTT.auth.username is not None and config.MQTT.auth.password is not None):
        client.username_pw_set(
            username=config.MQTT.auth.username,
            password=config.MQTT.auth.password
        )

    if (config.MQTT.cert is not None and config.MQTT.cert.required):
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

    prepare_client(client)

    if config.MQTT.keepalive:
        keepalive = config.MQTT.keepalive
    else:
        keepalive = 60

    client.connect(config.MQTT.host, config.MQTT.port, keepalive)
    
    return client

def cli():
    config_file = '/home/pmorch/.config/polyopen/config.yaml'
    config = yaml.safe_load(Path(config_file).read_bytes())
    config = Munch.fromDict(config)
    
    def prepare_client(client):
        
        def on_connect(client, userdata, flags, reason_code, properties):
            print(f"Connected with result code {reason_code}")
            # Subscribing in on_connect() means that if we lose the connection and
            # reconnect then subscriptions will be renewed.
            client.subscribe("pmorch")


        def on_message(client, userdata, msg):
            print(msg.topic+" "+str(msg.payload))

        client.on_connect = on_connect
        client.on_message = on_message

    client = create_client(config, prepare_client)
    client.loop_forever()