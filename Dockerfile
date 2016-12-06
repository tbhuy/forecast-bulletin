FROM ubuntu:latest
MAINTAINER Lamjed Ben Jabeur "Lamjed.Ben-Jabeur@irit.fr"
RUN apt-get update -y
RUN apt-get install -y python-pip python-dev build-essential
RUN pip install --upgrade pip
COPY . /sparkinclimate
WORKDIR /sparkinclimate
RUN pip install -r requirements.txt
ENTRYPOINT ["python"]
CMD ["server.py"]