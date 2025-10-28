# MQTT Protocol demonstration lab

This assignment is submitted by Koushik Sripathi (Roll no. 123CS0021)

The given task was to create a circuit with two sensors along with 2 LEDs.

Given below are the commands to execute and establish a MQTT connection between the sensors and the MQTT broker.

* Start the broker for topic: PIR(Passive IR sensor), MQ2 Gas sensor
`mosquitto_sub -h test.mosquitto.org -t "mqtt-demo2/motion"\n`
`mosquitto_sub -h test.mosquitto.org -t "mqtt-demo2/gas"\n`

* Turn on the LED
`mosquitto_pub -h test.mosquitto.org -t "mqtt-demo2/led1" -m "on"`

* Turn off the LED
`mosquitto_pub -h test.mosquitto.org -t "mqtt-demo2/led2" -m "off"`
