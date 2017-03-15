#!/bin/ash
sed s/_local_address_/$(hostname -i)/g exabgp.tmpl
