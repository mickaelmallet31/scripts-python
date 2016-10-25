#!/usr/bin/env python
# -*- coding: latin-1 -*-

import MySQLdb
import glob
import os
import yaml

# ========================================================================
# Functions
# ========================================================================


def get_list_builders():
    """Get the list of builders within buildbot"""

    list_builders = []
    for filename in glob.glob("../../../yamls/android/branches/*.yaml"):
        stream = open(filename, "r")
        docs = yaml.load_all(stream)
        for doc in docs:
            if 'android_branches.yaml' in doc:
                for k in doc['android_branches.yaml'].keys():
                    list_builders.append(k.split('.')[1])

    return(list_builders)


def get_query_sql(list_builder, duration_in_month=3):
    """Get the SQL query to be executed according to the list of builders and the date parameter"""

    return """
SELECT
    builder,
    count(builder)
FROM
(
    SELECT
        DISTINCT builder_name,
        substring_index(builder_name, "-", 1) as builder
    FROM
        builds
    WHERE
        finish_time >= unix_timestamp(date_sub(Now(),interval {} MONTH)) AND
        substring_index(builder_name,"-", 1) IN ({})
) AS T
GROUP BY
    builder
""".format(duration_in_month, list_builder)

# ========================================================================
# Main
# ========================================================================

# Change the directory
os.chdir(os.path.dirname(__file__))

# Open database connection
db = MySQLdb.connect("tlsisxdb003l.tl.intel.com", "metrics", "metrics", "metrics-prod")

# prepare a cursor object using cursor() method
cursor = db.cursor()

# set the duration
duration_in_month = 2

# get the list of builders
list_builders = get_list_builders()
string_builders = ','.join(["'{}'".format(x) for x in list_builders])

# execute SQL query using execute() method.
cursor.execute(get_query_sql(duration_in_month=duration_in_month, list_builder=string_builders))
result = dict(cursor.fetchall())

print "The following builders can be removed as there is no more activity on them since {} months:".format(duration_in_month)
for buildername in sorted(list_builders):
    if buildername not in result:
        print '. {}'.format(buildername)
