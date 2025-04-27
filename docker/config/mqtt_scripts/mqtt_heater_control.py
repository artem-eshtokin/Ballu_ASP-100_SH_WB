import paho.mqtt.client as mqtt

# MQTT параметры
BROKER_ADDRESS = "mqtt.cloud.rusklimat.ru"
BROKER_PORT = 8883
TOPIC_TARGET_TEMP = "rusclimate/<device_type>/<device_id>/state/temperature"
TOPIC_SENSOR_TEMP = "rusclimate/<device_type>/<device_id>/state/sensor/temperature"
TOPIC_MODE = "rusclimate/<device_type>/<device_id>/state/mode"
TOPIC_CURRENT_HEATER = "rusclimate/<device_type>/<device_id>/state/current_heater"

# TLS параметры
CAFILE = "./certs/ca.crt"
CERTFILE = "./certs/mosquitto.crt"
KEYFILE = "./certs/mosquitto.key"

target_temperature = None
sensor_temperature = None
mode = None

def on_message(client, userdata, message):
    global target_temperature, sensor_temperature, mode

    try:
        topic = message.topic
        payload = message.payload.decode()

        if topic == TOPIC_TARGET_TEMP:
            target_temperature = float(payload)
        elif topic == TOPIC_SENSOR_TEMP:
            sensor_temperature = float(payload)
        elif topic == TOPIC_MODE:
            mode = int(payload)

        if target_temperature is not None and sensor_temperature is not None and mode is not None:
            if mode == 0:   # Если режим выключен, то нагрев всегда выключен
                heater_status = 0
            else:
                heater_status = 1 if sensor_temperature <= target_temperature else 0

            client.publish(TOPIC_CURRENT_HEATER, payload=str(heater_status), qos=1)

    except Exception as e:
        print(f"Ошибка обработки сообщения: {e}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Успешно подключено к MQTT брокеру.")
        client.subscribe(TOPIC_TARGET_TEMP, qos=1)
        client.subscribe(TOPIC_SENSOR_TEMP, qos=1)
        client.subscribe(TOPIC_MODE, qos=1)
    else:
        print(f"Ошибка подключения, код: {rc}")

def main():
    client = mqtt.Client()
    client.tls_set(ca_certs=CAFILE, certfile=CERTFILE, keyfile=KEYFILE)
    client.tls_insecure_set(True)   # Включаем проверку для нестандартных сертификатов
    client.on_connect = on_connect
    client.on_message = on_message

    try:
        print("Подключение к брокеру...")
        client.connect(BROKER_ADDRESS, BROKER_PORT)
        client.loop_forever()   # Блокирует выполнение, пока не получим данные
    except Exception as e:
        print(f"Ошибка при подключении или работе клиента: {e}")

if __name__ == "__main__":
    main()
