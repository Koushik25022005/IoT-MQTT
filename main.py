from umqtt.simple import MQTTClient
from machine import Pin
import network
import ujson
import time
import dht

MQTT_BROKER = "test.mosquitto.org"
DHT_TOPIC = "mqtt-demo/dht"
PIR_TOPIC = "mqtt-demo/pir"
LED1_TOPIC = "mqtt-demo/led"
LED2_TOPIC = "mqtt-demo/irled2"
CLIENT_ID = "mark-mqtt-demo"

dht_sensor = dht.DHT22(Pin(33))
onboard_led = Pin(23, Pin.OUT)

PIR_PIN = 4                 # PIR input pin (choose a free GPIO)
pir_pin = Pin(PIR_PIN, Pin.IN)

onboard_led2 = Pin(2, Pin.OUT)  # second LED on a different pin

def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect('Wokwi-GUEST', '')
    while not wifi.isconnected():
        time.sleep(1)
    print("WiFi Connected:", wifi.ifconfig())
    return True

def message_callback(topic, msg):
    try:
        topic_str = topic.decode()
        msg_str = msg.decode().lower()
        if topic_str == LED1_TOPIC:
            if msg_str == "on":
                onboard_led.value(1)
            elif msg_str == "off":
                onboard_led.value(0)
        elif topic_str == LED2_TOPIC:
            if msg_str == "on":
                onboard_led2.value(1)
            elif msg_str == "off":
                onboard_led2.value(0)
    except Exception as e:
        print("Message Callback Error:", e)

def connect_mqtt():
    client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=1883)
    client.set_callback(message_callback)
    client.connect()
    client.subscribe(LED1_TOPIC)
    client.subscribe(LED2_TOPIC)
    print("Connected to MQTT. Subscribed to", LED1_TOPIC, LED2_TOPIC)
    return client

def read_and_publish_dht(client):
    try:
        dht_sensor.measure()
        temp = dht_sensor.temperature()
        hum = dht_sensor.humidity()
        reading = {
            "temperature": round(temp, 1),
            "humidity": round(hum, 1),
            "timestamp": time.time()
        }
        payload = ujson.dumps(reading)
        client.publish(DHT_TOPIC, payload)
        print("Published to", DHT_TOPIC, payload)
    except Exception as e:
        print("DHT Read/Publish Error:", e)

def read_and_publish_pir(client):
    try:
        motion = pir_pin.value()  # 1 when motion detected on many PIR modules
        if motion:
            reading2 = "Motion Detected"
            onboard_led2.value(1)
        else:
            reading2 = "No Motion Detected"
            onboard_led2.value(0)
        payload2 = ujson.dumps({"motion": reading2, "timestamp": time.time()})
        client.publish(PIR_TOPIC, payload2)
        print("Published to", PIR_TOPIC, payload2)
    except Exception as e:
        print("PIR Read/Publish Error:", e)

def main():
    if not connect_wifi():
        print("Failed to connect to WiFi!")
        return
    try:
        mqtt_client = connect_mqtt()
    except Exception as e:
        print("Failed to connect to MQTT:", e)
        return
    while True:
        try:
            mqtt_client.check_msg()
            read_and_publish_dht(mqtt_client)
            read_and_publish_pir(mqtt_client)
            time.sleep(5)
        except KeyboardInterrupt:
            print("\nShutting down...")
            break
        except Exception as e:
            print("Error in main loop:", e)
            time.sleep(1)

if __name__ == "__main__":
    main()