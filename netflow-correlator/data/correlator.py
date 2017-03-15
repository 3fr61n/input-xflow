import os
import socket
import json
from pprint import pprint
from kafka import KafkaConsumer
from kafka import KafkaProducer
from kafka.errors import KafkaError
import threading
import pytricia
import time

lock = threading.Lock() 
bgp_stats = {}
rib = {}

def request_bgp_route_refresh(**kwargs):
    peer = kwargs['peer']
    bgp_topic = 'jnpr.bgp.refresh.'+str(peer)
    kafka_address = socket.gethostbyname(os.environ['KAFKA_ADDR'])
    kafka_port = os.environ['KAFKA_PORT']
    producer = KafkaProducer(bootstrap_servers=[kafka_address+':'+kafka_port])
    producer.send(topic=bgp_topic,key='route-refresh',value='announce route-refresh ipv4 unicast')


def bgp_consumer():
#   It read kafka bgp topics and update BGP RIB structure and bgp stats
    bgp_topic = os.environ['BGP_KAFKA_TOPIC']
    kafka_address = socket.gethostbyname(os.environ['KAFKA_ADDR'])
    kafka_port = os.environ['KAFKA_PORT']
    global rib
    global bgp_stats
    consumer = KafkaConsumer(bgp_topic, bootstrap_servers=[ kafka_address+':'+kafka_port ])

    for message in consumer:
        # message value and key are raw bytes -- decode if necessary!
        # e.g., for unicode: `message.value.decode('utf-8')`
        json_thing = str(message.value.decode('ascii'))
        bgp_message = json.loads(json_thing)
        
        if bgp_message["type"] == "state":
            peer = bgp_message ["peer"]
            if bgp_message ["state"] == "down":
                #  Delete node from rib
                with lock:
                    if rib.has_key(peer): rib.pop(peer)
            elif bgp_message ["state"] == "up":
                #  Add node in rib  (check for duplicates)
                # Check if peer already exist on rib
                with lock:
                    if rib.has_key(peer): 
                        rib.pop(peer)
                    else:
                        rib[peer] = pytricia.PyTricia()
            elif bgp_message ["state"] == "connected":
                print("Bgp connected, nothing to do yet")  
            else:
                print("Unknown bgp state")  

        elif bgp_message["type"] == "update":
            print("Bgp update received")
            # Check if rib exists if not then request for a route-refresh
            peer = bgp_message["neighbor"]["ip"]
            print("from peer "+ peer)
            if not (rib.has_key(peer)):
                print ("peer not found on rib")
                with lock:
                    rib[peer] = pytricia.PyTricia()
                print ("Requesting route refresh to peer")
                request_bgp_route_refresh(peer=peer) 
                # Need to somehow ack that a route-refresh is being on the way, (what if it's being dampened)
            action = bgp_message["neighbor"]["message"]["update"].keys()[0]
            if action == "announce":
                bgp_next_hop = action = bgp_message["neighbor"]["message"]["update"]["announce"]["ipv4 unicast"]
            elif action == "withdraw":
                pass
            else:
                print ("Unknown update action")
            #prefix = bgp_message["neighbor"] == "state":
#            for announce in bgp_message["neighbor"]['message']:
#                for family in announce['famil']
            # If rib is not there request a session down or refresh to be sync
            # Extract relevant attributes..  (ASPATH)
        else:
            print("Unknown bgp message type")           

        if type(json_thing) is str:
            print(json.dumps(json.loads(json_thing), sort_keys=True, indent=4))
        else:
            print(json.dumps(json_thing, sort_keys=True, indent=4))
    
def netflow_consumer():
#   It read netflow bgp topics query the BGP RIB structure, send result to telegraf and update netflow stats
    bgp_topic = os.environ['NETFLOW_KAFKA_TOPIC']
    kafka_address = socket.gethostbyname(os.environ['KAFKA_ADDR'])
    kafka_port = os.environ['KAFKA_PORT']
    global rib
    global bgp_stats

    consumer = KafkaConsumer(bgp_topic, bootstrap_servers=[ kafka_address+':'+kafka_port ])

    for message in consumer:
        # message value and key are raw bytes -- decode if necessary!
        # e.g., for unicode: `message.value.decode('utf-8')`
        json_thing = str(message.value.decode('ascii'))
        if type(json_thing) is str:
            print(json.dumps(json.loads(json_thing), sort_keys=True, indent=4))
        else:
            print(json.dumps(json_thing, sort_keys=True, indent=4))


def internal_stats_publisher():
    global rib
    global bgp_stats    
    while True:
        print "rib:"
        pprint(rib)
        print "bgp_stats:"
        pprint(bgp_stats)
        time.sleep(10) 
##   each X sec it read internat stats and send meassurements to telegraf (statsd)

#threads = [threading.Thread(target=netflow_consumer), threading.Thread(target=bgp_consumer), threading.Thread(target=internal_stats_publisher)]
threads = [threading.Thread(target=bgp_consumer), threading.Thread(target=internal_stats_publisher)]

for t in threads:
    t.daemon = True    
    t.start()
for t in threads:
    t.join()

print("End")