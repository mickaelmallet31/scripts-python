#!/usr/bin/env python
# -*- coding: latin-1 -*-

import MySQLdb
import os
import yaml

# ========================================================================
# Functions
# ========================================================================


def get_list_testslaves():
    """ Get the list of testslaves declared in buildbot"""
    # Read the test_campaigns_exceptions.yaml file
    stream = open("../../../yamls/android/testslaves.yaml", "r")
    testslaves_table = []
    docs = yaml.load_all(stream)
    for doc in docs:
        testslaves_table.extend([x.replace('test', '') for x in doc.keys()])
    return testslaves_table


def get_query_sql(duration_in_month=3):
    """Get the SQL query to be executed according to the list of builders and the date parameter"""

    cmd = """
SELECT
    test_campaign_benches.name,
    builds.start_time
FROM
    test_campaign_benches
    INNER JOIN builds_test_campaigns ON test_campaign_benches.testCampaignID = builds_test_campaigns.testCampaignId
    INNER JOIN builds ON builds_test_campaigns.buildsetid = builds.buildsetid
WHERE
    builds.start_time >= unix_timestamp(date_sub(Now(),interval {} MONTH))
GROUP BY
    test_campaign_benches.name
""".format(duration_in_month)

    return cmd

# ========================================================================
# Main
# ========================================================================

# Change the directory
os.chdir(os.path.dirname(__file__))

# Get the list of declared test slaves
testslaves_table = get_list_testslaves()

# Open database connection
db = MySQLdb.connect("tlsisxdb003l.tl.intel.com", "metrics", "metrics", "metrics-prod")

# prepare a cursor object using cursor() method
cursor = db.cursor()

# set the duration
duration_in_month = 6

# execute SQL query using execute() method.
cursor.execute(get_query_sql(duration_in_month=duration_in_month))
result = dict(cursor.fetchall())
corrected_result = [testslave.split('.')[0] for testslave in result.keys()]
corrected_result.extend([
    'tlsispre999l',
    'tlacsci001l',
    'tlacsci001w',
    'tlacsci002l',
    'tlacsci002w',
])

print "The following testslaves can be removed as there is no more activity on them since {} months:".format(duration_in_month)
for testslave in sorted(testslaves_table):
    if testslave not in corrected_result:
        print '. {}'.format(testslave)
