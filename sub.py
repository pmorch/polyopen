import paho.mqtt.client as mqtt
import ssl


mosquitto_server = 'mqtt.morch.com'
port = 443
transport = 'websockets'  # or 'websockets'

username = 'pmorch'
password = 'asdfasdf'

def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.subscribe("pmorch")


def on_message(client, userdata, msg):
    print(msg.topic+" "+str(msg.payload))


mqttc = mqtt.Client(
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    transport=transport,
    client_id='pmorch_client'
)

mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.username_pw_set(username=username, password=password)

mqttc.tls_set(cert_reqs=ssl.CERT_REQUIRED)

mqttc.connect(mosquitto_server, port, 60)

mqttc.loop_forever()
