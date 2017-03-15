#!/usr/bin/env python
import json
import os
from sys import stdin, stdout
import datetime
import socket
import json

from kafka import KafkaProducer
from kafka.errors import KafkaError

def message_parser(line):
    # Parse JSON string  to dictionary
    temp_message = json.loads(line)

    # Convert Unix timestamp to python datetime
    #timestamp = datetime.fromtimestamp(temp_message['time'])
   # timestamp = datetime.datetime.fromtimestamp(temp_message['time'])
    timestamp = "23423"
    if temp_message['type'] == 'state':
        message = {
            'type': 'state',
            'time': timestamp,
            'peer': temp_message['neighbor']['ip'],
            'state': temp_message['neighbor']['state'],
        }

        return message

    if temp_message['type'] == 'keepalive':
        message = {
            'type': 'keepalive',
            'time': timestamp,
            'peer': temp_message['neighbor']['ip'],
        }

        return message

    # If message is a different type, ignore
    return temp_message 

counter = 0
bgp_topic = os.environ['BGP_KAFKA_TOPIC']
kafka_address = socket.gethostbyname(os.environ['KAFKA_ADDR'])
kafka_port = os.environ['KAFKA_PORT']
producer = KafkaProducer(bootstrap_servers=[kafka_address+':'+kafka_port],value_serializer=lambda m: json.dumps(m).encode('ascii'))

while True:
    try:
        line = stdin.readline().strip()
        
        # When the parent dies we are seeing continual newlines, so we only access so many before stopping
        if line == "":
            counter += 1
            if counter > 100:
                break
            continue
        counter = 0
        
        # Parse message, and if it's the correct type, store in the database
        message = message_parser(line)
        if message:
            producer.send(topic=bgp_topic, value=message) 

    except KeyboardInterrupt:
        pass
    except IOError:
        # most likely a signal during readline
        pass