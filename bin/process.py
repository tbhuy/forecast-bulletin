#!/usr/bin/env /python

import argparse
import configparser
import datetime
import os
import os.path
import sys
import json
import jsonpickle
from elasticsearch import Elasticsearch

sys.path.append('..')
sys.path.append(os.getcwd())

from sparkinclimate.text import TextUtils
from sparkinclimate.pdf import PDFDocument


# noinspection PyShadowingNames
def configuration():
    config = configparser.RawConfigParser()
    filename = None
    paths = ['config.ini', '../config.ini']
    for path in paths:
        if os.path.isfile(path):
            filename = path
            break
    if filename:
        config.read(filename)
    return config


if __name__ == '__main__':
    config = configuration()

    parser = argparse.ArgumentParser()
    parser.add_argument("-i", "--input", help="The output directory")
    args = parser.parse_args()
    args.input = args.input if args.input else 'dataset'

    es = Elasticsearch(["ns3038079.ip-5-135-160.eu"])
    for location in os.listdir(args.input):
        for file in os.listdir(args.input+'/'+location):
            (meteo,id,region,date) =file.replace('.pdf','').split('_')
            print(region+" "+date)
            document=PDFDocument(args.input+'/'+location+'/'+file)
            facts=document.facts(region=region, date=date)
            for fact in facts['facts']:
                #print(jsonpickle.encode(fact, unpicklable=False))
                fact.id=id
                try:
                    es.index(index="sparkinclimate", doc_type="facts",  body=jsonpickle.encode(fact, unpicklable=False))
                    pass
                except:
                    pass
