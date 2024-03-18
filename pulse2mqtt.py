#!/usr/bin/env python3
# encoding: utf-8
"""
pulse2mqtt.py
Created by Sascha Kloß on 2024-03-18.

base on pysml.py
Created by Christian Stade-Schuldt on 2014-10-25.

Change
MQTT Server IP in Line 45
PULSE_PASSWORD in Line 51

Follow https://forum.fhem.de/index.php?topic=133358.0
"""

import sys
import os
import datetime
import time
import re

from paho.mqtt import client as mqtt_client

import requests


# SML regexes
complete_message_regex = '1b1b1b1b01010101.*1b1b1b1b.{8}'
meter_108_regex = '070100010800ff.{24}(.{14})0177'
meter_208_regex = '070100020800ff.{16}(.{14})0177'
meter_167_regex = '070100100700ff.{16}(.{6})0177'

def connect_mqtt():
    def on_connect(client, userdata, flags, rc):
        if rc == 0:
            print("Connected to MQTT Broker!")
            client.publish ("tibberpulse/node", "ON")
            # client.subscribe(topic)
        else:
            print("Failed to connect, return code %d\n", rc)

    client = mqtt_client.Client("tibberpulse")
    client.on_connect = on_connect
    client.connect("192.168.178.x", 1883, 60)
    return client

def main():
  t = 1
  while t > 0:
    r = requests.get('http://tibber_host/data.json?node_id=1', auth=('admin', 'PULSE_PASSWORD'))
    #t -=1
    data = bytes(r.content).hex()
    # print (r.status_code)
    # print (data)

    if re.match(complete_message_regex, data):
      print ("MATCH")

      m108 = re.search(meter_108_regex, data)
      m208 = re.search(meter_208_regex, data)
      m167 = re.search(meter_167_regex, data)

      if m108 and m208 and m167:
        m167 = int(m167.group(1),16)
	      # check if value is negative
        if m167 > 0x7FFFF:
          m167 -= 0x1000000
          d108 = int(m108.group(1),16)/10000.0
          d208 = int(m208.group(1),16)/10000.0
          d167 = m167
                    
          client.publish("tibberpulse/" + "1.0.8", d108)
          client.publish("tibberpulse/" + "2.0.8", d208)
          client.publish("tibberpulse/" + "1.6.7", d167)
          print("{0}:{1}:{2}:{3}".format(d108,d208,d167,datetime.datetime.now().strftime('%d.%m.%Y')))

      time.sleep(1)
      client.loop()

if __name__ == '__main__':
    client = connect_mqtt()
    main()
