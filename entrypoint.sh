#!/bin/bash
# Download and process PDF dataset
#RUN python3 bin/wait --block 300
#RUN curl -XPUT http://localhost:9200/sparkinclimate -d @data/index_mapping.json
python3 /sparkinclimate/bin/dataset --out dataset
python3 /sparkinclimate/bin/process --input dataset --elasticsearch localhostdataset
python3 /sparkinclimate/bin/start-server --host 0.0.0.0 --port 7070
