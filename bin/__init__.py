#!/usr/bin/env python

import argparse
import configparser
import os
import sys

sys.path.append('..')
sys.path.append(os.getcwd())


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

    suffixes = ['.ndjson', '-statuses.log']
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--statuses_log", help="Statuses log file or directory that include statuses log file")
    parser.add_argument("-e", "--event", help="Event tag fo the event to be summarized for directory input")
    parser.add_argument("-o", "--out", help="The path of generate CSV file of pairs")
    parser.add_argument("-a", "--append", help="True if outpout should be append to an existing CSV file")
    parser.add_argument("-d", "--dataset", help="The dataset name")
    parser.add_argument("-n", "--from_event", help="Start from event")
    parser.add_argument("-m", "--to_event", help="End with event")
    parser.add_argument("-r", "--refresh", help="Refresh files if exists")
    args = parser.parse_args()