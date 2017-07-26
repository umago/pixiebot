FROM centos:centos7

ADD . /opt/pixiebot

RUN yum install -y epel-release

RUN yum install -y python python-devel python-tox

RUN cd /opt/pixiebot && tox -v -evenv --notest

CMD /opt/pixiebot/.tox/venv/bin/python -m pixiebot.bot
