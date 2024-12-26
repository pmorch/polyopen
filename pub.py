import paho.mqtt.client as mqtt
import ssl


mosquitto_server = 'mqtt.morch.com'

port = 443
transport = 'websockets'  # or 'websockets'

username = 'pmorch'
password = 'asdfasdf'


def on_connect(client, userdata, flags, reason_code, properties):
    print(f"Connected with result code {reason_code}")

def on_connect_fail(client, error):
    print('on_connect_fail')

mqttc = mqtt.Client(
    transport=transport,
    callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
    client_id='pmorch_pub')
mqttc.on_connect = on_connect
mqttc.on_connect_fail = on_connect_fail

mqttc.username_pw_set(username=username, password=password)

mqttc.tls_set(cert_reqs=ssl.CERT_REQUIRED)
mqttc.connect(mosquitto_server, port, 60)

mqttc.loop_start()

msg_info = mqttc.publish("pmorch", "my message", qos=1)
msg_info.wait_for_publish()

mqttc.disconnect()
mqttc.loop_stop()

