import paho.mqtt.client as mqtt
import time

# MQTT параметры
BROKER_ADDRESS = "mqtt.cloud.rusklimat.ru"
BROKER_PORT = 8883
TOPIC_TO_CHECK = "rusclimate/<device_type>/<device_id>/state/mode/meta/type"

# TLS параметры
CAFILE = "/app/certs/ca.crt"
CERTFILE = "/app/certs/mosquitto.crt"
KEYFILE = "/app/certs/mosquitto.key"

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Успешно подключено к MQTT брокеру.")
        client.subscribe(TOPIC_TO_CHECK, qos=1)
    else:
        print(f"Ошибка подключения, код: {rc}")

def on_message(client, userdata, message):
    global topic_exists
    topic_exists = True

def check_and_publish():
    global topic_exists
    topic_exists = False

    client = mqtt.Client()
    client.tls_set(ca_certs=CAFILE, certfile=CERTFILE, keyfile=KEYFILE)
    client.tls_insecure_set(True)
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print("Подключение к брокеру...")
        client.connect(BROKER_ADDRESS, BROKER_PORT, 60)
        client.loop_start()
        time.sleep(5)

        if not topic_exists:
            print(f"Топик {TOPIC_TO_CHECK} отсутствует, отправка 'Integer'")
            client.publish(TOPIC_TO_CHECK, payload="Integer", qos=1)
        else:
            print(f"Топик {TOPIC_TO_CHECK} найден")

        client.loop_stop()
        client.disconnect()
    except Exception as e:
        print(f"Ошибка подключения или обработки MQTT: {e}")

if __name__ == "__main__":
    while True:
        check_and_publish()
        time.sleep(1800)
