#!/bin/ash
ash /data/update-local-address.sh > /data/exabgp.conf
exabgp /data/exabgp.conf
#while true; do echo "bla"; sleep 1; done
