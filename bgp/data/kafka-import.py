#!/usr/bin/python

import os
import sys
import socket
import json
from pprint import pprint
from sys import stdout
import time
from kafka import KafkaConsumer
import argparse   # Used for argument parsing


################################################################################################
# Create and Parse Arguments
################################################################################################

full_parser = argparse.ArgumentParser()
full_parser.add_argument("-n", "--neighbor", help="BGP neighbor send route-refresh requests")
full_parser.add_argument("-i", "--minimum-interval", default=300, help="Minimum time between consecutive route-refresh request (seconds)")
dynamic_args = vars(full_parser.parse_args())

if dynamic_args['neighbor']:
	neighbor = dynamic_args['neighbor']
else:
    print('Missing <neighbor> option, so nothing to do')
    sys.exit(0)

route_refresh_dampening_timer =  dynamic_args['minimum_interval']

bgp_topic = 'jnpr.bgp.refresh.'+str(neighbor).strip()
kafka_address = socket.gethostbyname(os.environ['KAFKA_ADDR'])
kafka_port = os.environ['KAFKA_PORT']

latest_route_refresh_timestamp = 0

consumer = KafkaConsumer(bgp_topic, bootstrap_servers=[ kafka_address+':'+kafka_port ])

for message in consumer:
    if message.key == 'route-refresh':
        now = time.time()
        if ((now - latest_route_refresh_timestamp) > route_refresh_dampening_timer):
            latest_route_refresh_timestamp = now
            stdout.write( message.value + '\n')
            stdout.flush()
            time.sleep(1)
