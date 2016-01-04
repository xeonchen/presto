
import pytoml
import httplib
import urllib
import json
import os.path

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
    with open('alexa-top-10000-global.txt', 'r') as fin:
        tests = [x.strip('\n') for x in fin.readlines()]
    return tests

def log_response_id(location, index, domain, test_id, owner_key):
    filename = location+"_tests.csv"
    f = None
    if not os.path.exists(filename):
        f = open(filename, 'w')
    else:
        f = open(filename, 'a+')
        f.seek(0, 2) # go to end

    f.write(str(index) + ", "+ domain + ", " + test_id + ", " + owner_key + "\n")
    f.close()


def main():
    config = parse_config()
    print config

    tests = parse_domains()
    results = {}

    for i in range(config['start'], config['end']):
        for location in config['locations']:
            params = urllib.urlencode({'k': config['key'], 'location': location, 'url': tests[i], 'f': 'json', 'runs': 10})
            f = urllib.urlopen("http://www.webpagetest.org/runtest.php", params)
            response = json.loads(f.read())
            log_response_id(location, i, tests[i], response['data']['testId'], response['data']['ownerKey'])
            print response

if __name__ == '__main__':
	main()

