FROM ubuntu:22.04

RUN apt-get update;\
	apt-get install -y python3-pip python3-dev

COPY ./requirements.txt /requirements.txt

WORKDIR /
RUN pip3 install -r requirements.txt

COPY . /

ENTRYPOINT [ "/bin/sh" ]

CMD [ "./launcher.sh" ]
