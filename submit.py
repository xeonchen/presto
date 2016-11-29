#!/usr/bin/env python2.7
#
# This script submits requests to webpagetest.org in order to compare
# performance of web browsers in various conditions.
# Use config.toml to define the parameters.
# alexa-top-10000-global.txt is where the top domains are listed
# The output of this script will be several csv files, one for each location
# we have defined in the config. Once the checks are completed,
# use process_results.py or some other script to fetch the results and process
# them.
#

# TODO: use https://github.com/marcelduran/webpagetest-api
# as a better command line replacement.

import toml as pytoml
import httplib
import urllib
import json
import os.path
import sys
from datetime import datetime, date, time

def parse_config():
    with open('config.toml', 'rb') as fin:
        obj = pytoml.load(fin)
    if not obj['key']:
        raise Exception('Key must be defined in config file')
    if not 'start' in obj:
        obj['start'] = 0
    if not 'end' in obj:
        obj['end'] = 10000
    return obj

def parse_domains():
    tests = []
    with open('top100.txt', 'r') as fin:
        tests = [x.strip('\n') for x in fin.readlines()]
    return tests

def log_response_id(files, location, index, domain, test_id, owner_key):
    f = None
    if not location in files:
        filename = location+"_"+datetime.now().strftime("%m-%d-%H%M")+".csv"
        if not os.path.exists(filename):
            f = open(filename, 'w')
        else:
            f = open(filename, 'a+')
            f.seek(0, 2) # go to end

        files[location] = f
    else:
        f = files[location]
    f.write(str(index) + ", "+ domain + ", " + test_id + ", " + owner_key + "\n")


def main():
    config = parse_config()
    print config

    tests = parse_domains()
    results = {}

    files = {}

    for i in range(config['start'], config['end']):
        for location in config['locations']:
            if len(config['label'])>0:
                params = urllib.urlencode({'k': config['key'], 'location': location, 'url': tests[i], 'f': 'json', 'runs': 10, 'pingback': config['pingback'], 'label': config['label']})
            else:
                params = urllib.urlencode({'k': config['key'], 'location': location, 'url': tests[i], 'f': 'json', 'runs': 10, 'pingback': config['pingback']})
            f = urllib.urlopen(config['endpoint'], params)
            response = json.loads(f.read())
            print response
            log_response_id(files, location, i, tests[i], response['data']['testId'], response['data']['ownerKey'])

    for key in files:
        files[key].close()

def submit_one():
    config = parse_config()
    # domain, location, output
    domain = sys.argv[1]
    location = sys.argv[2]
    output = sys.argv[3]
    files = {}

    if not os.path.exists(output):
        f = open(output, 'w')
    else:
        f = open(output, 'a+')
        f.seek(0, 2) # go to end

    files[location] = f

    if len(config['label'])>0:
        params = urllib.urlencode({'k': config['key'], 'location': location, 'url': domain, 'f': 'json', 'runs': 10, 'pingback': config['pingback'], 'label': config['label']})
    else:
        params = urllib.urlencode({'k': config['key'], 'location': location, 'url': domain, 'f': 'json', 'runs': 10, 'pingback': config['pingback']})
    f = urllib.urlopen(config['endpoint'], params)
    response = json.loads(f.read())
    log_response_id(files, location, 0, domain, response['data']['testId'], response['data']['ownerKey'])
    print response

    for key in files:
        files[key].close()

if __name__ == '__main__':
    if len(sys.argv) == 1:
        main()
    else:
        submit_one()

