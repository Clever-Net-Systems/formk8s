FROM centos:7

ARG MYSQL_HOST_ARG=undefined
ENV MYSQL_HOST=$MYSQL_HOST_ARG

# TODO USER
RUN yum install -y epel-release && \
    yum install -y mysql-connector-python.noarch

WORKDIR /srv/monapp

COPY client.py .

EXPOSE 8000
CMD python client.py
