import paho.mqtt.client as mqtt
import ssl

from . import config_loader, mqttclient

def pub():
    config = config_loader.load()

    config.clientId += '-pub'

    def on_connect(client, userdata, flags, reason_code, properties):
        print(f"Connected with result code {reason_code}")

    def on_connect_fail(client, error):
        print('on_connect_fail')

    def prepare_client(client):
        client.on_connect = on_connect
        client.on_connect_fail = on_connect_fail

    client = mqttclient.create_client(config, prepare_client)

    client.loop_start()

    msg_info = client.publish("pmorch", "my message", qos=1)
    msg_info.wait_for_publish()

    client.disconnect()
    client.loop_stop()