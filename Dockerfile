FROM openwhisk/java8action:latest

MAINTAINER Lamjed Ben Jabeur "Lamjed.Ben-Jabeur@irit.fr"
MAINTAINER Ba Huy Tran "ba-huy.tran@irit.fr"



LABEL vendor=IRIT \
    fr.irit.iris.sparkinclimate.is-beta= \
    fr.irit.iris.sparkinclimate.is-production=  \
    fr.irit.iris.sparkinclimate.version="0.0.1b" \
    fr.irit.iris.sparkinclimate.release-date="2019-06-11"

RUN apt-get update && apt-get install -y \
    software-properties-common \
    wget \
    curl \
    libperl4-corelibs-perl

# Install Python 3 and NLTK
RUN apt-get install -y python3 python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install -U nltk
RUN pip3 install requests
RUN pip3 install argparse
RUN pip3 install configparser
RUN pip3 install python-csv 
RUN pip3 install elasticsearch
RUN python3 -m nltk.downloader punkt
RUN python3 -m nltk.downloader stopwords
RUN python3 -m nltk.downloader snowball_data

# Install Java 1.8
#RUN add-apt-repository ppa:webupd8team/java -y && \
#    apt-get update && \
#    echo oracle-java7-installer shared/accepted-oracle-license-v1-1 select true | /usr/bin/debconf-set-selections && \
#    apt-get install -y oracle-java8-installer && \
#    apt-get clean
#ENV JAVA_HOME /usr/lib/jvm/java-8-oracle


# Configure project
COPY . /sparkinclimate
WORKDIR /sparkinclimate
RUN pip3 install -r requirements.txt
RUN chmod a+x bin/*


# Install Elasticsearch 5
RUN wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.1.1.tar.gz
RUN tar -xzf elasticsearch-5.1.1.tar.gz
RUN useradd -m -d /home/elasticsearch elasticsearch
RUN chown -R elasticsearch:elasticsearch elasticsearch-5.1.1/
USER elasticsearch
WORKDIR elasticsearch-5.1.1/
RUN ./bin/elasticsearch -d
USER root
WORKDIR ..

# Install Treetagger
WORKDIR treetagger
RUN pwd
RUN ls -ls
#RUN wget http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/tree-tagger-linux-3.2.1.tar.gz \
#    http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/tagger-scripts.tar.gz \
#    http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/install-tagger.sh
COPY tree-tagger-linux-3.2.1.tar.gz .
COPY tagger-scripts.tar.gz .
COPY install-tagger.sh .
RUN tar -zxvf tree-tagger-linux-3.2.1.tar.gz
RUN tar -zxvf tagger-scripts.tar.gz
WORKDIR lib
#RUN wget http://dl.nlpub.ru/treetagger/english-par-linux-3.2-utf8.bin.gz \
#    http://www.cis.uni-muenchen.de/~schmid/tools/TreeTagger/data/english-chunker.par.gz
COPY english-par-linux-3.2-utf8.bin.gz .
COPY english-chunker.par.gz .
COPY french-par-linux-3.2-utf8.bin.gz .
COPY french-chunker-par-linux-3.2-utf8.bin.gz .
RUN gunzip english-par-linux-3.2-utf8.bin.gz
RUN gunzip english-chunker.par.gz
RUN gunzip french-par-linux-3.2-utf8.bin.gz
RUN gunzip french-chunker-par-linux-3.2-utf8.bin.gz
RUN mv english-par-linux-3.2-utf8.bin english-utf8.par
#RUN mv english-chunker-par-linux-3.2-utf8.bin english-chunker.par
RUN mv french-par-linux-3.2-utf8.bin french-utf8.par
RUN mv french-chunker-par-linux-3.2-utf8.bin french-chunker.par
WORKDIR ..
RUN sh install-tagger.sh
ENV PATH=$PATH:/sparkinclimate/treetagger/cmd:/sparkinclimate/treetagger/bin
ENV PATH=${PATH}:/usr/bin/python3
ENV PYTHONPATH={PYTHONPATH}:/sparkinclimate
WORKDIR ..
COPY entrypoint.sh /
RUN chmod +x /entrypoint.sh
CMD ["/entrypoint.sh"]
