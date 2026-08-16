FROM python:3.12

ARG MYSQL_HOST_ARG=undefined
ENV MYSQL_HOST=$MYSQL_HOST_ARG
ENV PYTHONUNBUFFERED=1
ENV TZ=Europe/Zurich

WORKDIR /srv/monapp

COPY --chown=1000:1000 client.py .

RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone && \
    useradd -m dev --uid 1000 && \
    pip install mysql.connector && \
    pip install reload && \
    chown -R dev:dev /srv/monapp && \
    chmod +x /srv/monapp/client.py

USER dev
CMD ["reload","/srv/monapp/client.py"]

