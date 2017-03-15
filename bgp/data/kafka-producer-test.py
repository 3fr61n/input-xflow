#!/usr/bin/python

import os
import socket
import json

from kafka import KafkaProducer
from kafka.errors import KafkaError

bgp_topic = os.environ['BGP_KAFKA_TOPIC']
kafka_address = socket.gethostbyname(os.environ['KAFKA_ADDR'])
kafka_port = os.environ['KAFKA_PORT']

producer = KafkaProducer(bootstrap_servers=[kafka_address+':'+kafka_port])
producer.send(topic=bgp_topic,value='kakaka')

producer = KafkaProducer(bootstrap_servers=[kafka_address+':'+kafka_port],value_serializer=lambda m: json.dumps(m).encode('ascii'))
producer.send(topic=bgp_topic, value={'key': 'value'})