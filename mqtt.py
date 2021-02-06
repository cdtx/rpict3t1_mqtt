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
        mqtt_client= paho.Client("current")
        mqtt_client.connect(MQTT_BROKER, MQTT_PORT)

        line = ser.readline().decode('utf-8').strip()
        line_values = line.split()

        topics = (
            '/current/nodeid',
            '/current/1', 
            '/current/2', 
            '/current/3', 
        )

        if len(line_values) >= 4:
            values = map(float, line_values)

            # Shape a dictionary of all the values we want to send in one shot using function publish.multiple.
            mqtt_message = [[k, v] for k,v in zip(topics, values)]

            # Send the message
            publish.multiple(mqtt_message)
    
    except:
        traceback.print_exc()
            
    finally:
        ser.close()
        mqtt_client.disconnect()

if __name__ == '__main__':
    run()
