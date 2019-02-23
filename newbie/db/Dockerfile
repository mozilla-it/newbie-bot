FROM postgres
ENV POSTGRES_DB newbie
ENV PGDATA /var/lib/postgresql/data/pgdata
COPY psql_dump.sql /docker-entrypoint-initdb.d/