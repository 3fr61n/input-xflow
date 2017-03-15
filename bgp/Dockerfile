FROM juniper/pyez:2.0.1

WORKDIR /source
USER root

## To be removed once change merge upstream
RUN apk add --no-cache ca-certificates && \
    update-ca-certificates
RUN apk add --no-cache wget git bind-tools supervisor python py-pip

ARG EXABGP_VERSION=3.4.18
ARG KAFKA_PYTHON_VERSION=1.3.2

########################
### Install kafka    ###
########################

RUN     pip install "kafka-python==$KAFKA_PYTHON_VERSION"

########################
### Install exabgp   ###
########################

RUN     pip install "exabgp==$EXABGP_VERSION"

RUN mkdir /data
ADD data /data/
WORKDIR /data

RUN  chmod +x /data/start-input-bgp.sh
COPY supervisord.conf /etc/supervisord.conf

ENTRYPOINT ["supervisord", "--nodaemon", "--configuration", "/etc/supervisord.conf"]
