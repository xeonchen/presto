#
# This script generates a JS file which contains the following content:
#
# var testData = {
#   "name": "test1",
#   "data": [
#   {
#    "domain": " google.com",
#    "firefoxId": "160104_KM_Q6F",
#    "chromeId": "160104_C4_Q6G"
#    "firstDiff": 77,
#    "secondDiff": 679,
#   }
# ]};
# displayTable(testData);
#
# Make sure you define a displayTable function which processes the results
#


import pytoml
import httplib
import urllib
import json

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

def main():
    config = parse_config()
    browser_tests = {}

    # Parse the test files in order to get the testIDs
    for location in config['locations']:
        f = open(location+'_tests.csv', 'r')
        res = [x.strip('\n') for x in f.readlines()]

        for line in res:
            [index, domain, test_id, key] = line.split(',')
            target = {}
            if int(index) in browser_tests:
                target = browser_tests[int(index)]
            target[location] = test_id
            target['domain'] = domain
            browser_tests[int(index)] = target

        f.close()

    # This is where we output relevant data from the results
    output = open('out.js', 'w')
    content = {}
    content['name'] = '1-100'

    data = []
    for index in range(config['start'], config['end']):
        firstValid = True
        secondValid = True

        entry = {}
        entry['domain'] = browser_tests[index]['domain']
        firstDiff = 0
        secondDiff = 0

        for location in config['locations']:
            jsonurl = 'http://www.webpagetest.org/jsonResult.php'
            params = urllib.urlencode({'test': browser_tests[index][location].strip()})
            f = urllib.urlopen(jsonurl, params)

            response = json.loads(f.read())
            target = response['data']['median'] # firstView / repeatView
            try:
                firstDiff = -firstDiff + response['data']['median']['firstView']['SpeedIndex']
            except:
                firstValid = False
                print "Can't find firstView median for index %d location %s" % (index, location)

            try:
                secondDiff = -secondDiff + response['data']['median']['repeatView']['SpeedIndex']
            except:
                secondValid = False
                print "Can't find repeatView median for index %d location %s" % (index, location)

            if location.find(":C") != -1:
                entry['chromeId'] = browser_tests[index][location].strip()
            else:
                entry['firefoxId'] = browser_tests[index][location].strip()

        entry['firstDiff'] = firstDiff
        entry['secondDiff'] = secondDiff

        if firstValid and secondValid:
            data.append(entry)

    content['data'] = data
    output.write('var testData = '+json.dumps(content)+';')
    output.write('displayTable(testData);')
    output.close()


if __name__ == '__main__':
	main()

