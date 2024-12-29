import paho.mqtt.client as mqtt
import ssl
from rich import print

from . import config_loader


def create_client(config, prepare_client = None):
    pass

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        transport=config.MQTT.transport,
        client_id=config.clientId
    )
    if (config.MQTT.auth.username is not None and config.MQTT.auth.password is not None):
        client.username_pw_set(
            username=config.MQTT.auth.username,
            password=config.MQTT.auth.password
        )

    if (config.MQTT.cert is not None and config.MQTT.cert.required):
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

    if prepare_client is not None:
        prepare_client(client)

    if config.MQTT.keepalive:
        keepalive = config.MQTT.keepalive
    else:
        keepalive = 60

    client.connect(config.MQTT.host, config.MQTT.port, keepalive)
    
    return client

def cli():
    
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

    config = config_loader.load()
    client = create_client(config, prepare_client)
    client.loop_forever()