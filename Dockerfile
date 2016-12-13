FROM ubuntu:latest
MAINTAINER Lamjed Ben Jabeur "Lamjed.Ben-Jabeur@irit.fr"
RUN apt-get update -y
RUN apt-get install -y wget
RUN apt-get install -y python3 python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install -U nltk
RUN python3 -m nltk.downloader punkt
RUN python3 -m nltk.downloader stopwords
RUN python3 -m nltk.downloader snowball_data


COPY . /sparkinclimate
RUN rm -r sparkinclimate/cache
WORKDIR /sparkinclimate

WORKDIR treetagger
RUN sh install-tagger.sh
ENV PATH=$PATH:/sparkinclimate/treetagger/cmd:/sparkinclimate/treetagger/bin
WORKDIR ..

RUN pip3 install -r requirements.txt


RUN chmod a+x bin/*
RUN ./bin/dataset --out dataset

ENTRYPOINT ["python3"]
CMD ["server.py"]


