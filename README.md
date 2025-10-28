# MQTT Protocol demonstration lab

The given task was to create a circuit with two sensors along with the DHT22 sensor.

Given below are the commands to execute and establish a connection between the sensors and the MQTT broker.

* Start the broker for topic: PIR(Passive IR sensor), DHT22(Digital Humidity and Temperature sensor)
`mosquitto_sub -h test.mosquitto.org -t "mqtt-demo/pir"`
`mosquitto_sub -h test.mosquitto.org -t "mqtt-demo/dht"`

* Turn on the LED
`mosquitto_pub -h test.mosquitto.org -t "mqtt-demo/led" -m "on"`

* Turn off the LED
`mosquitto_pub -h test.mosquitto.org -t "mqtt-demo/led" -m "off"`

**Note:**
The circuit diagram contains 2 leds where one LED is independent and the other LED is interfaced with the Passive IR sensor to show the presence/detection of motion. 
