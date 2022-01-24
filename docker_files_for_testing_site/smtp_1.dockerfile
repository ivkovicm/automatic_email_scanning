FROM alpine:latest
RUN apk update && apk add bash && apk add postfix && apk add dovecot
SHELL ["/bin/bash", "-c"]
RUN mkdir /run/postgresql && chown postgres:postgres /run/postgresql
RUN su postgres
RUN mkdir /var/lib/postgresql/data && chmod 0700 /var/lib/postgresql/data
RUN initdb -D /var/lib/postgresql/data && echo "host all all 0.0.0.0/0 md5" >> /var/lib/postgresql/data/pg_hba.conf && echo "listen_addresses='*'" >> /var/lib/postgresql/data/postgresql.conf
RUN su postgres -c 'pg_ctl start -D /var/lib/postgresql/data'
RUN exit
RUN touch /etc/local.d/postgres-custom.start && chmod +x /etc/local.d/postgres-custom.start
RUN echo "#!/bin/sh\nmkdir /run/postgresql\nchown postgres:postgres /run/postgresql\nsu postgres -c 'pg_ctl start -D /var/lib/postgresql/data'"
RUN rc-update add local default && openrc