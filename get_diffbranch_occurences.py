#!/usr/bin/env python

import glob
import os
import os.path
import re
import sys
import yaml

# Change the current directory
os.chdir(os.path.dirname(sys.argv[0]))

data_config = {}
# Read the diffbranch configuration files
for filename in glob.glob("../../../yamls/android/diffbranch/*.yaml"):
    stream = open(filename, "r")
    docs = yaml.load_all(stream)
    for doc in docs:
        for config in doc['diffbranch.yaml'].keys():
            data_config[config] = {'date': 'NA', 'url': 0, 'counter': 0, 'scheduled': doc['diffbranch.yaml'][config]['schedule']['enabled']}
sorted_x = sorted(data_config)

output_file = "/tmp/output_file.txt"
os.system('zgrep "absp/builders/diffbranch/builds/.*/steps/diffbranch/logs" /var/log/apache2/ssl_access.log* > {}'.format(output_file))

data_url = {}
for line in open(output_file, "r"):
    # Skip lines with sys_cactus@
    if re.search('sys_cactus@', line):
        continue

    res = re.search("/absp/builders/diffbranch/builds/([^/]+)/steps/diffbranch/logs", line)
    if res is not None:
        url = format(res.group(1))
        if url not in data_url:
            data_url[url] = 1
        else:
            data_url[url] += 1

for url, count in data_url.items():
    destfile = "/tmp/diffbranch_{}.txt".format(url)

    if os.path.isfile(destfile):
        with open(destfile) as f:
            config = f.readline().strip()
            date_build = f.readline().strip()
            url = f.readline().strip()
    else:
        os.system('wget "https://buildbot.tl.intel.com/absp/builders/diffbranch/builds/{}" -O {}'.format(url, destfile))
        found = 0
        regexp2 = '<td class="left protected">diffbranch</td>'
        regexp1 = '<tr><td class="left">End</td><td>(.*)</td></tr>'
        regexp3 = '<td class="value">(.*)</td>'

        for line in open(destfile):
            line = line.rstrip()
            if found == 0:
                # Get the date
                res = re.search(regexp1, line)
                if res is not None:
                    date_build = res.group(1)
                    found = 1
            elif found == 1:
                # Looks for diffbranch line
                res = re.search(regexp2, line)
                if res is not None:
                    found = 2
            elif found == 2:
                # Get the configuration
                res = re.search(regexp3, line)
                if res is not None:
                    config = res.group(1)
                    found = 3
                    break
        if found == 0:
            print "Did not find the reg '{}' in {}".format(regexp1, destfile)
            exit(1)
        elif found == 1:
            print "Did not find the reg '{}' in {}".format(regexp2, destfile)
            exit(1)
        elif found == 2:
            print "Did not find the reg '{}' in {}".format(regexp3, destfile)
            exit(1)

        fd = open(destfile, "w")
        fd.write("{}\n{}\n{}\n".format(config, date_build, url))
        fd.close()

    if config in data_config:
        if int(url) >= int(data_config[config]['url']):
            data_config[config]['url'] = url
            data_config[config]['date'] = date_build
        data_config[config]['counter'] += data_url[url]

print '\n\n(JIRA format)'
print '|Configuration|Occurences|Scheduled?|Last build accessed|Build Date|'
for config in sorted_x:
    value = data_config[config]
    print "|{}|{}|{}| https://buildbot.tl.intel.com/absp/builders/diffbranch/builds/{} |{}|".format(config, value['counter'], value['scheduled'], value['url'], value['date'])

print '\n\n(CSV format)'
print 'Configuration,Occurences,Scheduled?,Last build accessed, Build date'
for config in sorted_x:
    value = data_config[config]
    print "{},{},{},https://buildbot.tl.intel.com/absp/builders/diffbranch/builds/{},{}".format(config, value['counter'], value['scheduled'], value['url'], value['date'])
