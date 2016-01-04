#
# This scripts processes the data supplied by webpagetest.org runs
# Previously to running this script, one must run the submit.py script which
# triggers these tests. After testing is completed, this script will parse
# the results and aggregate them in a file named complete.csv
#

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
            browser_tests[int(index)] = target

        f.close()

    # This is where we output relevant data from the results
    output = open('complete.csv', 'w')

    # On each line, we display the median results for both browsers
    for location in config['locations']:
        output.write('"Test ID",')
        output.write('"Date","Time","Event Name","URL","Load Time (ms)","Time to First Byte (ms)","unused","Bytes Out","Bytes In","DNS Lookups","Connections","Requests","OK Responses","Redirects","Not Modified","Not Found","Other Responses","Error Code","Time to Start Render (ms)","Segments Transmitted","Segments Retransmitted","Packet Loss (out)","Activity Time(ms)","Descriptor","Lab ID","Dialer ID","Connection Type","Cached","Event URL","Pagetest Build","Measurement Type","Experimental","Doc Complete Time (ms)","Event GUID","Time to DOM Element (ms)","Includes Object Data","Cache Score","Static CDN Score","One CDN Score","GZIP Score","Cookie Score","Keep-Alive Score","DOCTYPE Score","Minify Score","Combine Score","Bytes Out (Doc)","Bytes In (Doc)","DNS Lookups (Doc)","Connections (Doc)","Requests (Doc)","OK Responses (Doc)","Redirects (Doc)","Not Modified (Doc)","Not Found (Doc)","Other Responses (Doc)","Compression Score","Host","IP Address","ETag Score","Flagged Requests","Flagged Connections","Max Simultaneous Flagged Connections","Time to Base Page Complete (ms)","Base Page Result","Gzip Total Bytes","Gzip Savings","Minify Total Bytes","Minify Savings","Image Total Bytes","Image Savings","Base Page Redirects","Optimization Checked","AFT (ms)","DOM Elements","PageSpeed Version","Page Title","Time to Title","Load Event Start","Load Event End","DOM Content Ready Start","DOM Content Ready End","Visually Complete (ms)","Browser Name","Browser Version","Base Page Server Count","Base Page Server RTT","Base Page CDN","Adult Site","Run","Cached","Speed Index",')

    # We add a row of titles to the end. Will be used later, to compare each 2 results
    output.write(',"","Load Time (ms)","Time to First Byte (ms)","unused","Bytes Out","Bytes In","DNS Lookups","Connections","Requests","OK Responses","Redirects","Not Modified","Not Found","Other Responses","Error Code","Time to Start Render (ms)","Segments Transmitted","Segments Retransmitted","Packet Loss (out)","Activity Time(ms)","Descriptor","Lab ID","Dialer ID","Connection Type","Cached","Event URL","Pagetest Build","Measurement Type","Experimental","Doc Complete Time (ms)","Event GUID","Time to DOM Element (ms)","Includes Object Data","Cache Score","Static CDN Score","One CDN Score","GZIP Score","Cookie Score","Keep-Alive Score","DOCTYPE Score","Minify Score","Combine Score","Bytes Out (Doc)","Bytes In (Doc)","DNS Lookups (Doc)","Connections (Doc)","Requests (Doc)","OK Responses (Doc)","Redirects (Doc)","Not Modified (Doc)","Not Found (Doc)","Other Responses (Doc)","Compression Score","Host","IP Address","ETag Score","Flagged Requests","Flagged Connections","Max Simultaneous Flagged Connections","Time to Base Page Complete (ms)","Base Page Result","Gzip Total Bytes","Gzip Savings","Minify Total Bytes","Minify Savings","Image Total Bytes","Image Savings","Base Page Redirects","Optimization Checked","AFT (ms)","DOM Elements","PageSpeed Version","Page Title","Time to Title","Load Event Start","Load Event End","DOM Content Ready Start","DOM Content Ready End","Visually Complete (ms)","Browser Name","Browser Version","Base Page Server Count","Base Page Server RTT","Base Page CDN","Adult Site","Run","Cached","Speed Index",\n')
    #                  CT2-F2 - This is the formula for load time comparison between 2 browsers
    #                           Extend it to other rows and columns to get the full picture

    for index in browser_tests:
        lines = ["", ""]
        for location in config['locations']:
            url = 'http://www.webpagetest.org/result/'+browser_tests[index][location].strip()+'/page_data.csv'
            f = urllib.urlopen(url)
            csv = f.read().split('\n')


            # We also load the json results, just to get which runs are median
            # without crunching all the data.
            # Also, it seems that some fields such as DNS lookups only show up in the CSV

            jsonurl = 'http://www.webpagetest.org/jsonResult.php'
            params = urllib.urlencode({'test': browser_tests[index][location].strip()})
            f = urllib.urlopen(jsonurl, params)

            response = json.loads(f.read())
            target = response['data']['median'] # firstView / repeatView
            medianIndexFirst = response['data']['median']['firstView']['run']
            medianIndexRepeat = response['data']['median']['repeatView']['run']
            csvFirstIndex = medianIndexFirst * 2 - 1
            csvRepeatIndex = medianIndexRepeat * 2

            # First view median
            lines[0] = lines[0] + browser_tests[index][location].strip() + ',' + csv[csvFirstIndex].strip()
            # Repeat view median
            lines[1] = lines[1] + browser_tests[index][location].strip() + ',' + csv[csvRepeatIndex].strip()

        output.write(lines[0] + "\n" )
        output.write(lines[1] + "\n" )

    output.close()


if __name__ == '__main__':
	main()

