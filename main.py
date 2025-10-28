from machine import Pin
import network
import ujson
import time
from umqtt.simple import MQTTClient

# MQTT Configuration
MQTT_BROKER = "test.mosquitto.org"
CLIENT_ID = "mqtt-demo"
TOPIC_MOTION = "mqtt-demo/motion"
TOPIC_GAS = "mqtt-demo/gas"
TOPIC_LED1 = "mqtt-demo/led1"  # controls gas LED
TOPIC_LED2 = "mqtt-demo/led2"  # controls motion LED

# Pin Configuration
LED1_PIN = 23  # Gas indicator LED
LED2_PIN = 2   # Motion indicator LED
PIR_PIN = 4    # PIR sensor output
GAS_PIN = 25   # MQ-2 DOUT digital pin

# Initialize pins
led_gas = Pin(LED1_PIN, Pin.OUT)
led_motion = Pin(LED2_PIN, Pin.OUT)
pir_sensor = Pin(PIR_PIN, Pin.IN)
gas_sensor = Pin(GAS_PIN, Pin.IN)

def connect_wifi():
    wifi = network.WLAN(network.STA_IF)
    wifi.active(True)
    wifi.connect('Wokwi-GUEST', '')
    
    # Wait for connection with timeout
    timeout = 10
    while timeout > 0 and not wifi.isconnected():
        print("Connecting to WiFi...")
        time.sleep(1)
        timeout -= 1
    
    if wifi.isconnected():
        print("WiFi connected:", wifi.ifconfig())
        return True
    else:
        print("Failed to connect to WiFi")
        return False

def message_callback(topic, msg):
    try:
        topic_str = topic.decode('utf-8')
        msg_str = msg.decode('utf-8').lower()
        print("MQTT message:", topic_str, msg_str)
        
        if topic_str == TOPIC_LED1:
            led_gas.value(1 if msg_str == "on" else 0)
            print(f"Gas LED turned {'ON' if msg_str == 'on' else 'OFF'}")
        elif topic_str == TOPIC_LED2:
            led_motion.value(1 if msg_str == "on" else 0)
            print(f"Motion LED turned {'ON' if msg_str == 'on' else 'OFF'}")
    except Exception as e:
        print("Message Callback Error:", e)

def connect_mqtt():
    try:
        client = MQTTClient(CLIENT_ID, MQTT_BROKER, port=1883, keepalive=60)
        client.set_callback(message_callback)
        client.connect()
        client.subscribe(TOPIC_LED1)
        client.subscribe(TOPIC_LED2)
        print("Connected to MQTT broker and subscribed to control topics.")
        return client
    except Exception as e:
        print("MQTT connection failed:", e)
        return None

def publish_motion(client):
    try:
        motion = pir_sensor.value()
        msg = "Motion Detected" if motion else "No Motion"
        # Only update LED if not controlled by MQTT
        # led_motion.value(motion)  # Commented out to avoid conflict with MQTT control
        payload = ujson.dumps({"motion": msg, "timestamp": time.time()})
        client.publish(TOPIC_MOTION, payload)
        print("Published motion:", payload)
    except Exception as e:
        print("Error publishing motion:", e)

def publish_gas(client):
    try:
        gas_state = gas_sensor.value()
        # MQ-2 output is LOW (0) when gas detected
        detected = (gas_state == 0)
        msg = "Gas Detected" if detected else "No Gas"
        # Only update LED if not controlled by MQTT
        # led_gas.value(1 if detected else 0)  # Commented out to avoid conflict with MQTT control
        payload = ujson.dumps({"gas": msg, "timestamp": time.time()})
        client.publish(TOPIC_GAS, payload)
        print("Published gas:", payload)
    except Exception as e:
        print("Error publishing gas:", e)

def main():
    # Connect to WiFi
    if not connect_wifi():
        print("Failed to connect to WiFi")
        return

    # Connect to MQTT
    client = connect_mqtt()
    if client is None:
        print("Failed to connect to MQTT broker")
        return

    print("Starting main loop...")
    
    try:
        while True:
            try:
                # Check for MQTT messages
                client.check_msg()
                
                # Publish sensor data
                publish_motion(client)
                publish_gas(client)
                
                # Wait before next iteration
                time.sleep(5)
                
            except Exception as e:
                print("Error in main loop:", e)
                # Try to reconnect
                try:
                    client = connect_mqtt()
                    if client is None:
                        print("Failed to reconnect to MQTT")
                        time.sleep(10)
                except:
                    print("Reconnection failed")
                    time.sleep(10)
                    
    except KeyboardInterrupt:
        print("Program stopped by user.")
    finally:
        # Cleanup
        client.disconnect()
        print("Disconnected from MQTT")

if __name__ == "__main__":
    main()