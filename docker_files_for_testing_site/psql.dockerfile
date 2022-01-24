FROM alpine:latest

EXPOSE 5432
VOLUME ["/DATABASE"]
ENV PGDATA="/DATABASE"

RUN apk update && apk upgrade --no-cache
RUN apk add bash --no-cache && apk add postgresql --no-cache && apk add openrc --no-cache

SHELL ["/bin/bash", "-c"]

RUN mkdir /run/postgresql && chown postgres:postgres /run/postgresql && chown postgres:postgres /DATABASE
RUN touch /etc/local.d/postgres-custom.start && chmod +x /etc/local.d/postgres-custom.start
RUN echo "#!/bin/sh\nmkdir /run/postgresql\nchown postgres:postgres /run/postgresql\nsu postgres -c 'postgres -D /var/lib/postgresql/data -c config_file=/var/lib/postgresql/data/postgresql.conf'"
RUN rc-update add local default && openrc

USER postgres

RUN mkdir /var/lib/postgresql/data && chmod 0700 /var/lib/postgresql/data
RUN initdb -D /var/lib/postgresql/data && echo "host all all 0.0.0.0/0 md5" >> /var/lib/postgresql/data/pg_hba.conf && echo "listen_addresses='*'" >> /var/lib/postgresql/data/postgresql.conf
RUN pg_ctl start -D /var/lib/postgresql/data && psql --command "CREATE USER docker with SUPERUSER PASSWORD 'docker';" && createdb -O docker docker

CMD ["postgres", "-D", "/var/lib/postgresql/data", "-c", "config_file=/var/lib/postgresql/data/postgresql.conf"]
