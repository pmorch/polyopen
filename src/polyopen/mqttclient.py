import ssl

import paho.mqtt.client as mqtt
from rich import print

from . import config_loader


def create_client(config, prepare_client=None):
    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        transport=config.MQTT.transport.value,
        client_id=config.clientId,
    )
    if config.MQTT.auth.username is not None and config.MQTT.auth.password is not None:
        client.username_pw_set(
            username=config.MQTT.auth.username, password=config.MQTT.auth.password
        )

    if config.MQTT.cert is not None and config.MQTT.cert.required:
        client.tls_set(cert_reqs=ssl.CERT_REQUIRED)

    if prepare_client is not None:
        prepare_client(client)

    if config.MQTT.keepalive:
        keepalive = config.MQTT.keepalive
    else:
        keepalive = 60

    client.connect(config.MQTT.host, config.MQTT.port, keepalive)

    return client
