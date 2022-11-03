FROM centos:7

ENV MYSQL_HOST=undefined

# TODO WORKDIR et USER
RUN yum install -y epel-release && \
    yum install -y mysql-connector-python.noarch

WORKDIR /srv/monapp

COPY client.py .

EXPOSE 8000
CMD python client.py
