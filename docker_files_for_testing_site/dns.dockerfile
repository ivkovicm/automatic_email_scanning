FROM alpine:latest

RUN apk update --no-cache && apk upgrade --no-cache && apk add bash --no-cache && apk add bind --no-cache
WORKDIR /etc/bind
SHELL ["/bin/bash", "-c"]
RUN mkdir -p /var/lib/bind/ && touch /var/lib/bind/bind.log && chown named:named /var/lib/bind/bind.log && touch /var/run/named/named.pid && chown root:named /var/run/named/named.pid && chmod 0770 /var/run/named/named.pid
RUN mkdir zone1

COPY "zone1.com.zone" zone1
COPY named1.conf ./named.conf

CMD ["named", "-f", "-c", "/etc/bind/named.conf", "-u", "named"]