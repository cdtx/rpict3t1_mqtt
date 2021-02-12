#!/usr/bin/env python3

import traceback
import serial
import paho.mqtt.client as paho
import paho.mqtt.publish as publish

MQTT_BROKER = '127.0.0.1'
MQTT_PORT = 1883

def run():
    try:
        ser = serial.Serial('/dev/ttyAMA0', 38400)
        line = ser.readline().decode('utf-8').strip()
        line_values = line.split()

        topics = (
            '/current/nodeid',
            '/current/1', 
            '/current/2', 
            '',
            # '/current/3', 
        )

        # Convert all read values to float
        values = map(float, line_values)

        # Shape a nested list of all the [topic, value] we want to send in one shot using function publish.multiple.
        mqtt_message = [[topic, value] for topic,value in zip(topics, values) if topic]

        # Send the message
        publish.multiple(hostname=MQTT_BROKER, port=MQTT_PORT, mqtt_message)
    
    except:
        traceback.print_exc()
            
    finally:
        ser.close()
        mqtt_client.disconnect()

if __name__ == '__main__':
    run()
