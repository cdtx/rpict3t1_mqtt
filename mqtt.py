#!/usr/bin/env python3

import json
import traceback
import serial
import paho.mqtt.client as paho
import paho.mqtt.publish as publish

MQTT_BROKER = '127.0.0.1'
MQTT_PORT = 1883

def run():
    try:
        # ser = serial.Serial('/dev/ttyAMA0', 38400)
        # line = ser.readline().decode('utf-8').strip()
        # line_values = line.split()
        line_values = "1 2 3 4 5".split()

        # All domoticz options : https://www.domoticz.com/wiki/Domoticz_API/JSON_URL%27s
        # Prepare the messages to send
        mqtt_messages = (
            {'Idx':1},
            {'Idx':2},
            {'Idx':3},
            None,
            # '/current/3', 
        )

        # Fill the field nvalue
        for value, message in zip(line_values, mqtt_messages):
            if not message:
                continue
            else:
                message['nvalue'] = float(value)

        # Send the message
        # remove None messages
        mqtt_messages = [mess for mess in mqtt_messages if mess]
        import pdb; pdb.set_trace()
        publish.multiple(mqtt_messages, hostname=MQTT_BROKER, port=MQTT_PORT)
    
    except:
        traceback.print_exc()
            

if __name__ == '__main__':
    run()
