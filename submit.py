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
from datetime import datetime

def parse_config():
    global config

    with open('config.toml', 'rb') as fin:
        obj = pytoml.load(fin)

    config = { 'start': 0, 'end': 10000 }
    config.update(obj)

def parse_domains():
    with open('top100.txt', 'r') as fin:
        return [x.strip('\n') for x in fin.readlines()]

def log_response_id(location, index, domain, test_id, owner_key):
    f = logs[location]
    line = '%s, %s, %s, %s\n' % (index, domain, test_id, owner_key)
    f.write(line)

def get_param(location, url, label=None):
    params = {
        'f': 'json',
        'location': location,
        'priority' : config.get('priority', '5'),
        'runs': config['runs'],
        'url': url
    }
    if config.get('key'):
        params['k'] = config['key']
    if config.get('pingback'):
        params['pingback'] = config['pingback']
    if label:
        params['label'] = label

    return urllib.urlencode(params)

def submit_all():
    tests = parse_domains()

    for i in range(config['start'], config['end']):
        for j, location in enumerate(config['locations']):
            try:
                label = config['labels'][j]
            except:
                label = None
            submit_one(tests[i], location, label, i)

def submit_one(domain, location, label=None, index=0, output=None):
    if location not in logs:
        if output is None:
            output = '%s_%s.csv' % (location, datetime.now().strftime("%m-%d-%H%M"))

        if not os.path.exists(output):
            f = open(output, 'w')
        else:
            f = open(output, 'a+')
            f.seek(0, 2) # go to end

        logs[location] = f

    param = get_param(location, domain, label)
    print param
    f = urllib.urlopen(config['endpoint'], param)
    response = json.loads(f.read())
    print response
    if response['statusCode'] == 200:
        log_response_id(location, index, domain, response['data']['testId'], response['data']['ownerKey'])

def main(args):
    global logs
    logs = {}

    parse_config()

    if len(args) == 1:
        submit_all()
    elif len(args) == 4:
        submit_one(args[1], args[2], args[3])

    for f in logs.itervalues():
        f.close()

if __name__ == '__main__':
    main(sys.argv)

