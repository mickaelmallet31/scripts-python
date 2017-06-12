#!/usr/bin/env python

import re
import os
import requests
import json
import sys

#
# Excepted format for the .gitmodules file:
# [submodule "meta-genivi-dev"]
#    path = meta-genivi-dev
#    url = http://github.com/genivi/meta-genivi-dev.git

input_file = "list_project_path_names.txt"
if len(sys.argv) > 1:
    input_file = sys.argv[1]

# Values for tldlab23
token = "Ws6qyNwFo5Racz-jWvQC"
github_url = "tldlab23.tl.intel.com"

#
# To get the namespaces ID, execute the following command for example:
# curl --header "PRIVATE-TOKEN: eLzF-u6Pjmy-hFzUyZck" "https://gitlab.forestscribe.intel.com/api/v3/namespaces"
#

# Values for gitlab marathon
token = "eLzF-u6Pjmy-hFzUyZck"
token = "KkHWZXxeH9NeCcMcPd9E"
github_url = "gitlab.forestscribe.intel.com"
organization = "forestscribe-android"
namespace_id = 11
branch = "origin/HEAD"

#organization = "forestscribe-yocto"
#namespace_id = 19
#branch =  "m/master"
print "set -x"

#os.system('repo list > {}'.format(input_file))
for line in open(input_file, "r"):
    line = line.strip()
    (path, name) = line.split(' : ')
    name = re.sub('/','_', name)
    name = name.replace('.', '-')
    cmd = ""

    # To generate the script that will create all the repos
    if 0:
        cmd += "curl --header \"PRIVATE-TOKEN: {}\" -X POST \"https://{}/api/v3/projects?name={}&visibility=public&namespace_id={}\"".format(token, github_url, name, namespace_id)
        print cmd

    if 0:
        # On gitlab . in project names is not supported
        print "git submodule add -f git@{}:{}/{}.git {}".format(github_url, organization, name, path)

    # To push on github
    if 1:
        cmd = "cd {}\n".format(path)
        #cmd += "export GIT_SSL_NO_VERIFY=1"
        #cmd += "git fetch --unshallow\n"
        #cmd += "git branch -D master; git checkout {} -b master\n".format(branch)
        cmd += "git remote remove origin\n"
        cmd += "git remote add origin git@{}:{}/{}\n".format(github_url, organization, name)
        cmd += "git push origin HEAD:master\n"
        cmd += "cd -\n"
        print cmd

    # To generate the script that will create all the repos
    if 0:
        r = requests.post('http://{}/api/v3/orgs/{}/repos'.format(github_url, organization),
                data=json.dumps({'name':name}),
                verify=False)
        print r
