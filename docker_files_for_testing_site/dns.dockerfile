FROM alpine:latest

RUN apk update --no-cache && apk upgrade --no-cache && apk add bash --no-cache && apk add bind --no-cache && apk add bind-doc --no-cache && apk add openrc --no-cache

WORKDIR /etc/bind
RUN mkdir zone1
COPY "zone1.com.zone" zone1
COPY named1.conf ./named.conf
SHELL ["/bin/bash", "-c"]
RUN rc-update add named && mkdir /run/openrc && touch /run/openrc/softlevel
RUN mkdir -p /var/lib/bind/ && touch /var/lib/bind/bind.log && chown named:named /var/lib/bind/bind.log && touch /var/run/named/named.pid && chown root:named /var/run/named/named.pid && chmod 0770 /var/run/named/named.pid
CMD ["bash"]

#RUN mkdir -p /var/lib/bind/ && touch /var/lib/bind/bind.log && chown named:named /var/lib/bind/bind.log && named -c /etc/bind/named.conf -u named
#CMD ["bash"]