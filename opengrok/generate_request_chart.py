#!/usr/bin/env python

import re
import sys

#
# This script parses the ssl_access.log and retrieves the list of projects ordered by the nb of searches
# Usefull to determine which should be removed the next time
#

#filename = sys.arg[1]
filename = "/etc/apache2/logs/ssl_access.log"

skipped_project = [
    "BUILDBOT_PROD",
    "BUILDBOT_MAIN",
    "WEBAPPS_MAIN",
    "BUILDBOT_STAGING"
]

data = {}
for line in open(filename, "r"):
    m = re.search('\[([^:]+).*"([^"]+)" ([0-9]+)', line)
    if m is not None:
        date = m.group(1)
        string = m.group(2)
        http_errorcode = int(m.group(3))
        if http_errorcode == 200:
            project = ""
            m = re.search("/source/(xref)?/search.+project=([^\s]+)", string)
            if m is not None:
                project = m.group(2)
                #print "Spy 1", line, project
            else:
                m = re.search("/source/xref/([^/ ]+)/", string)
                if m is not None:
                    project = m.group(1)
                    #print "Spy 2", line, project
            if project != "" and project not in skipped_project:
                if project not in data:
                    data[project] = 1
                else:
                    data[project] += 1

#print "<html><body><table border='1' cellpadding='3' cellspacing='0'><tr style='background-color:black; color: white;'><td>Project</td><td>Nb of requests for this project</td></tr>"
for project in sorted(data, key = data.get, reverse=True):
    #print "<tr><td>%s</td><td>%s</td></tr>" % (project, data[project])
    print "%s :  %s" % (project, data[project])
#print "</table></body></html>"
