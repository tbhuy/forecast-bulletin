WORKDIR /sparkinclimate

RUN ls -ls
# Download and process PDF dataset
#RUN python3 bin/wait --block 300
#RUN curl -XPUT http://localhost:9200/sparkinclimate -d @data/index_mapping.json
RUN python3 ./bin/dataset --out dataset
RUN python3 ./bin/process --input dataset --elasticsearch localhostdataset
RUN python3 ./bin/start-server --host 0.0.0.0 --port 7070
