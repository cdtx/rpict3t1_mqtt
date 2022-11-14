#!/usr/bin/env python3
import os
import traceback
import configparser
import serial
from paho.mqtt.client import Client as PahoClient

from pymqtt_hass.items import Device

current_folder = os.path.dirname(os.path.abspath(__file__))
CONFIG_FILE = 'config.ini'
PYMQTT_HASS_CONFIG_FILE = 'pymqtt_hass_config.json'

def get_config():
    ret = {}
    config = configparser.ConfigParser()
    config.read(os.path.join(current_folder, CONFIG_FILE))

    ret['MQTT_HOST'] = config.get('MQTT', 'HOST')
    ret['MQTT_PORT'] = config.getint('MQTT', 'PORT', fallback=1883)
    ret['MQTT_USERNAME'] = config.get('MQTT', 'USERNAME')
    ret['MQTT_PASSWORD'] = config.get('MQTT', 'PASSWORD')

    return ret

def run():
    config = get_config()


    # Initialize MQTT client
    client = PahoClient()
    # Set the client options
    client.enable_logger()
    client.username_pw_set(config['MQTT_USERNAME'], config['MQTT_PASSWORD'])
    # Connect the mqtt client
    client.connect(config['MQTT_HOST'], config['MQTT_PORT'])

    # Get the configured home-assistant device
    device = Device(client, os.path.join(current_folder, PYMQTT_HASS_CONFIG_FILE))
    # Send the hass's device discovery
    device.send_discovery()

    try:
        # Read values from the serial line
        ser = serial.Serial('/dev/ttyAMA0', 38400)
        line = ser.readline().decode('utf-8').strip()
        line_values = line.split()

        # Convert all read values to float
        values = list(map(float, line_values))

        # Drop the node id and temperature if any
        values = values[1:4]

        device_topic = device.get_device_topic()

        # Publish the total consumed power
        topic = '/'.join([
            device_topic,
            'power',
            'total',
        ])
        client.publish(topic, sum(values))
        client.loop()

        # Publish each value (one per phase) on appropriate topic
        for i, value in enumerate(values):
            topic = '/'.join([
                device_topic,
                'power',
                'phase_{}'.format(i+1),
            ])
            client.publish(topic, value)
            client.loop()

    except:
        traceback.print_exc()
            
    finally:
        ser.close()

if __name__ == '__main__':
    run()
