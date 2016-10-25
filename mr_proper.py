#!/usr/bin/env python

#
# Imports
#
import argparse
import base64
import datetime
import httplib2
import os
import re
import smtplib
import socket
import sys
import tempfile
import yaml

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import dirname
from os.path import expanduser

#
# Constants
#
RETENTION_RELEASE = 0
RETENTION_DAILY = 1
RETENTION_OTHERS = 2
RETENTION_METABUILDBOT = 3

ENVIRONMENT_PROD = "prod"
ENVIRONMENT_STAGE = "staging"
ENVIRONMENT_DEV = "dev"

AGE = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
RED = '\033[91m'
BOLD = '\033[1m'
REGULAR = '\033[0m'
UNDERLINE = '\033[4m'

#
# Global variables
#
# Parameters to delete the builds
data = [
    {
        'repo': 'irda-{site}',
        'pattern': '*',
        'retention': RETENTION_RELEASE,
        'keep': '"@keep": {"$ne": "true"}',
        'depth': 3,
        'do_not_execute': True,
    },
    {
        'repo': '{cactus_path_keyword}-{site}',
        'pattern': "build/eng-builds/*/weekly",
        'retention': RETENTION_RELEASE,
        'keep': '"@keep" : {"$ne" : "true"}',
        'depth': 6,
        'do_not_execute': True,
    },
    {
        'repo': '{cactus_path_keyword}-{site}',
        'pattern': "build/eng-builds/*/daily",
        'retention': RETENTION_DAILY,
        'keep': '"@keep" : {"$ne" : "true"}',
        'depth': 6,
        'keep_last_build': True,
        # Test: keep the last one for daily builds : only delete this build not the following one
        # even if the retention policy makes this build obsolete
        "unit_test": {
            "retention_date": "2016-08-25T",
            "results": [
                {
                    "repo": "cactus-absp-jf",
                    "path": "build/eng-builds/1A_OSAG_c/PSI/daily",
                    "name": "20160425_0000",
                    "type": "folder",
                    "size": 0,
                    "created": "2016-04-25T06:48:32.674-07:00",
                    "created_by": "jgozalv",
                    "modified": "2016-04-25T06:48:32.674-07:00",
                    "modified_by": "jgozalv",
                    "updated": "2016-04-25T06:48:32.674-07:00"
                },
                {
                    "repo": "cactus-absp-jf",
                    "path": "build/eng-builds/1A_OSAG_c/PSI/daily",
                    "name": "20160426_0000",
                    "type": "folder",
                    "size": 0,
                    "created": "2016-04-26T06:48:32.674-07:00",
                    "created_by": "jgozalv",
                    "modified": "2016-04-26T06:48:32.674-07:00",
                    "modified_by": "jgozalv",
                    "updated": "2016-04-26T06:48:32.674-07:00"
                },
            ],
        },
    },
    {
        'repo': '{cactus_path_keyword}-{site}',
        'pattern': "*-release_candidate",
        'retention': RETENTION_OTHERS,
        'keep': '"@keep" : {"$ne" : "true"}',
        'depth': 2,
        # 'do_not_execute': True,
    },
    {
        'repo': '{cactus_path_keyword}-{site}',
        'pattern': "*-latest",
        'retention': RETENTION_OTHERS,
        'keep': '"@keep" : {"$ne" : "true"}',
        'depth': 2,
        'keep_last_build': True,
        # 'do_not_execute': True,
    },
    {
        'repo': '{cactus_path_keyword}-{site}',
        'pattern': "*-engineering",
        'retention': RETENTION_OTHERS,
        'keep': '"@keep" : {"$ne" : "true"}',
        'depth': 2,
        # Test: delete only the build that expired
        "unit_test": {
            "retention_date": "2016-08-25T",
            "results": [
                {
                    "repo": "cactus-absp-tl",
                    "path": "bxtp_ivi-engineering",
                    "name": "65",
                    "type": "folder",
                    "size": 0,
                    "created": "2016-08-20T05:47:28.995-07:00",
                    "modified": "2016-08-20T05:47:28.995-07:00",
                    "updated": "2016-08-20T05:47:28.995-07:00"
                },
                {
                    "repo": "cactus-absp-tl",
                    "path": "bxtp_ivi-engineering",
                    "name": "66",
                    "type": "folder",
                    "size": 0,
                    "created": "2016-08-21T05:47:28.995-07:00",
                    "modified": "2016-08-21T05:47:28.995-07:00",
                    "updated": "2016-08-21T05:47:28.995-07:00"
                },
            ],
        },
    },
    {
        'repo': '{cactus_path_keyword}-{site}',
        'pattern': "*-autobuild",
        'retention': RETENTION_OTHERS,
        'keep': '"@keep" : {"$ne" : "true"}',
        'depth': 2,
        # 'do_not_execute': True,
    },
    {
        'repo': '{cactus_path_keyword}-{site}',
        'pattern': "*-preintegration",
        'retention': RETENTION_OTHERS,
        'keep': '"@keep" : {"$ne" : "true"}',
        'depth': 2,
        # 'do_not_execute': True,
    },
    {
        'repo': '{cactus_path_keyword}-{site}',
        'pattern': "*-mergebridge",
        'retention': RETENTION_OTHERS,
        'keep': '"@keep" : {"$ne" : "true"}',
        'depth': 2,
        # 'do_not_execute': True,
    },
    {
        'repo': '{cactus_path_keyword}-{site}',
        'pattern': "*-custom_diff_manifest",
        'retention': RETENTION_OTHERS,
        'keep': '"@keep" : {"$ne" : "true"}',
        'depth': 2,
        # 'do_not_execute': True,
    },
    {
        'repo': '{cactus_path_keyword}-{site}',
        'pattern': "port-bug-fix",
        'retention': RETENTION_OTHERS,
        'keep': '"@keep" : {"$ne" : "true"}',
        'depth': 2,
        # 'do_not_execute': True,
    },
    {
        'repo': '{cactus_path_keyword}-{site}',
        'pattern': "*-mergerequest",
        'retention': RETENTION_OTHERS,
        'keep': '"@keep" : {"$ne" : "true"}',
        'depth': 2,
        'keep_last_build': True,
        # Test: check that the rexexp is working for other builders
        "unit_test": {
            "retention_date": "2016-08-25T",
            "results": [
                {
                    "repo": "cactus-absp-tl",
                    "path": "bxtp_ivi-mergerequest",
                    "name": "65",
                    "type": "folder",
                    "size": 0,
                    "created": "2016-07-23T05:47:28.995-07:00",
                    "modified": "2016-07-23T05:47:28.995-07:00",
                    "updated": "2016-07-23T05:47:28.995-07:00"
                },
                {
                    "repo": "cactus-absp-tl",
                    "path": "bxtp_ivi-mergerequest",
                    "name": "66",
                    "type": "folder",
                    "size": 0,
                    "created": "2016-07-24T05:47:28.995-07:00",
                    "modified": "2016-07-24T05:47:28.995-07:00",
                    "updated": "2016-07-24T05:47:28.995-07:00"
                },
            ],
        },
    },
    {
        'repo': 'cactus-metabuildbot-{site}',
        'pattern': "*",
        'retention': RETENTION_METABUILDBOT,
        'keep': '"@keep" : {"$ne" : "true"}',
        'depth': 2,
        # 'do_not_execute': True,
    },
]

# ==================================================
#
# Functions
#
# ==================================================


#
# get_retention_parameter
#
def get_retention_parameter(choice):
    ''' Get the site list, the cactus path keyword and the retention duration per build type '''

    if choice == ENVIRONMENT_PROD:
        # For prod environment
        stream = open("{}/../../../yamls/android/sites.yaml".format(dirname(sys.argv[0])), "r")
        sites_tab = {}
        docs = yaml.load_all(stream)
        for doc in docs:
            for target, value in doc.items():
                sites_tab[target] = value['artifactory_server']['artifactory_url']

        # Set the artifactory cactus path
        cactus_path_keyword = 'cactus-absp'

        # Define retention
        retention_table = ['12m', '3m', '7d', '1m']

    elif choice == ENVIRONMENT_STAGE:
        # For staging environment
        sites_tab = {
            'jf': 'https://artidevjf.jf.intel.com',
            'sh': 'https://artidevsh.sh.intel.com',
            'tl': 'https://artidevtl.tl.intel.com',
        }

        # Set the artifactory cactus path
        cactus_path_keyword = 'cactus-absp-staging'

        # Define retention
        retention_table = ['10d', '10d', '10d', '30d']

    elif choice == ENVIRONMENT_DEV:
        # For dev environment
        sites_tab = {
            'tl': 'https://artidevtl.tl.intel.com',
        }

        # Set the artifactory cactus path
        cactus_path_keyword = 'cactus-absp-main'

        # Define retention
        retention_table = ['30d', '30d', '30d', '30d']

    else:
        print 'Wrong choice'
        exit(1)

    return(sites_tab, cactus_path_keyword, retention_table)

#
# sendmail
#


def sendmail(text_to_be_send, subject, sender, receivers):
    ''' Function to send the report by mail '''

    # Complete the mail with the footer
    text_to_be_send += "<br/><font size='-1'><i># (generated by '{}' with '{}' account on '{}' machine)</i></font>".format(" ".join(sys.argv), os.environ['LOGNAME'], socket.gethostname())
    smtpObj = smtplib.SMTP("smtp.intel.com")
    message = MIMEMultipart('alternative')
    message["Subject"] = subject
    message["From"] = sender
    message["To"] = receivers
    part = MIMEText(text_to_be_send, 'html')
    message.attach(part)
    smtpObj.sendmail(sender, receivers, message.as_string())

#
# get_date_build
#


def get_date_build(retention):
    ''' Returns the date of the oldest builds to be kept '''

    d = datetime.date.today()

    result = re.search('([0-9]+)m', retention)
    if result is not None:
        month_delta = result.group(1)
        d = d - datetime.timedelta(365 / 12 * int(month_delta))
    else:
        result = re.search('([0-9]+)d', retention)
        if result is not None:
            days_delta = result.group(1)
            d = d - datetime.timedelta(int(days_delta))
        else:
            result = re.search('([0-9]+)w', retention)
            if result is not None:
                week_delta = result.group(1)
                d = d - datetime.timedelta(int(week_delta) * 7)

    return "%04d-%02d-%02dT" % (d.year, d.month, d.day)

#
# get_list_builds_to_be_deleted
#


def get_list_builds_to_be_deleted(build_param, builder, retention_date, artifactory_server):
    ''' Get the list of builds to be deleted '''
    previous_path = ""
    msg = ""
    cmd_delete_build = ""
    keep_last_build = ('keep_last_build' in builder and builder['keep_last_build'])

    for build, value in build_param.items():
        if build == 'results':
            # For latest and daily builds keep the last one even if it is out of
            # retention policy
            for index in value:
                if keep_last_build:
                    if previous_path != "":
                        if previous_path == index['path'] and cmd_delete_build != "":
                            msg += "{}\n".format(cmd_delete_build)
                        cmd_delete_build = ""
                    previous_path = index['path']

                if retention_date == "" or index['created'] < retention_date:
                    cmd_delete_build = """curl -X DELETE -v {}/artifactory/{}/{}/{}
curl -X DELETE -v {}/artifactory/api/trash/clean/{}/{}/{}
""".format(artifactory_server, index["repo"], index["path"], index["name"], artifactory_server, index["repo"], index["path"], index["name"])

                if keep_last_build is False and cmd_delete_build != "":
                    msg += "{}\n".format(cmd_delete_build)
                    cmd_delete_build = ""

    # Returnt the delete command
    return msg

#
# looks_for_builds_to_be_deleted
#


def looks_for_builds_to_be_deleted(choice, sites_tab, cactus_path_keyword, retention_table):
    ''' Query the specified artifactory servers to find out which builds could be deleted '''

    msg = """
# =============================================================================================
# For {} environment
# ============================================================================================= """.format(choice)
    print msg

    for site in sites_tab:
        print "Treat the request for {} ...".format(site)

        for builder in data:

            # Skip builder if not requested
            if 'do_not_execute' in builder:
                continue

            # Define the criteria
            criteria = ""

            criteria += '"type":"folder"'
            if 'repo' in builder:
                criteria += ',\n"repo": "%s"' % (builder['repo'].replace('{site}', site).replace('{cactus_path_keyword}', cactus_path_keyword))
            if 'depth' in builder:
                criteria += ',\n"depth": "%s"' % (builder['depth'])
            if 'pattern' in builder:
                criteria += ',\n"path": {"$match" : "%s"}' % (builder['pattern'])
            if 'retention' in builder:
                retention_date = get_date_build(retention_table[builder['retention']])
            else:
                retention_date = ""
            if 'keep' in builder:
                criteria += ',\n%s' % (builder['keep'])

            # Define the RAW data
            DATA = '''items.find(
{
%s
}
)
.sort({"$asc" : ["path", "created"]})''' % (criteria)

            print DATA
            sys.exit(0)
            try:
                URL = "{}/artifactory/api/search/aql".format(sites_tab[site])

                msg += "\n# Request on {}:\n# {}\n# Retention date: {}\n\n".format(URL, " ".join(DATA.split('\n')), retention_date)

                # Disable the SSL certification validation
                h = httplib2.Http(".cache", disable_ssl_certificate_validation=True)

                # Launch the request
                resp, content = h.request(
                    URL,
                    "POST",
                    body=DATA,
                    headers={"Authorization": "Basic %s" %
                             base64.encodestring('%s:%s' % (USERNAME, PASSWORD))}
                )
            except:
                raise
                msg += "Issue with request for {}. Skipped".format(sites_tab[site])
                continue

            if resp['status'] == '401':
                msg += '# Error in the used credentials for {} (username={}, password={}).'\
                    'Thanks to double check'.format(sites_tab[site], USERNAME, PASSWORD)
                break
            elif resp['status'] != '200':
                msg += '# Issue with the query for {}. Below is the status of the query:\n{}'.\
                    format(sites_tab[site], resp)
                break

            build_param = yaml.load(content)

            msg += get_list_builds_to_be_deleted(build_param, builder, retention_date, sites_tab[site])

    # Return the script commands
    return(msg)

#
# unit_test
#


def unit_test():
    ''' Unit test function'''

    expected_result_unit_test = """curl -X DELETE -v artifactory_server/artifactory/cactus-absp-jf/build/eng-builds/1A_OSAG_c/PSI/daily/20160425_0000
curl -X DELETE -v artifactory_server/artifactory/api/trash/clean/cactus-absp-jf/build/eng-builds/1A_OSAG_c/PSI/daily/20160425_0000

curl -X DELETE -v artifactory_server/artifactory/cactus-absp-tl/bxtp_ivi-mergerequest/65
curl -X DELETE -v artifactory_server/artifactory/api/trash/clean/cactus-absp-tl/bxtp_ivi-mergerequest/65

curl -X DELETE -v artifactory_server/artifactory/cactus-absp-tl/bxtp_ivi-engineering/65
curl -X DELETE -v artifactory_server/artifactory/api/trash/clean/cactus-absp-tl/bxtp_ivi-engineering/65

"""

    result_unit_test = ""
    for builder in data:
        if 'unit_test' in builder:
            result_unit_test += get_list_builds_to_be_deleted(builder['unit_test'], builder, builder['unit_test']['retention_date'], "artifactory_server")

    assert expected_result_unit_test == result_unit_test, "Did not find the expected result:\n. expected_result_unit_test =\n{}\n\n. result_unit_test = \n{}".format(expected_result_unit_test, result_unit_test)

# ==================================================
#
# Main
#
# ==================================================

# Set the choices to null
choices = []

# Parse the parameters
parser = argparse.ArgumentParser()
parser.add_argument("--clean_prod", help="clean the prod environment",
                    required=False, action="store_true")
parser.add_argument("--clean_stage", help="clean the staging environment",
                    required=False, action="store_true")
parser.add_argument("--clean_dev", help="clean the dev environment",
                    required=False, action="store_true")
parser.add_argument("--unit_test", help="",
                    required=False, action="store_true")

args = parser.parse_args()
if args.clean_prod:
    choices.append(ENVIRONMENT_PROD)
if args.clean_stage:
    choices.append(ENVIRONMENT_STAGE)
if args.clean_dev:
    choices.append(ENVIRONMENT_DEV)
if args.unit_test:
    unit_test()
    sys.exit(0)

# Read the username and password from the $HOME/.curlrc
home = expanduser("~")
for line in open('{}/.curlrc'.format(home)):
    line = line.strip()
    m = re.search('^user\s+(.+):(.+)', line)
    if m is not None:
        USERNAME = m.group(1)
        PASSWORD = m.group(2)

# Execute the retention according to the choices
script_cmd = ""
for choice in choices:

    # Get the retention parameters
    (sites_tab, cactus_path_keyword, retention_table) = get_retention_parameter(choice)

    # looks for the builds to be deleted
    script_cmd += looks_for_builds_to_be_deleted(choice, sites_tab, cactus_path_keyword, retention_table)

# Prepare the deletion script
_, deletion_script = tempfile.mkstemp(".txt", os.path.basename(sys.argv[0]))
fd = open(deletion_script, "w")
fd.write(script_cmd)
fd.close()

# Send the mail
msg = "Execution of the following script done (see {}):<br/><pre>{}</pre>".format(deletion_script, script_cmd)
sendmail(msg, "[MR_PROPER]", "cactus-infrastructure@intel.com", "cactus-infrastructure@intel.com")

# Execute the deletion script
os.system("bash {}".format(deletion_script))
