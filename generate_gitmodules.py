#!/usr/bin/env python

import re
import os
import requests
import json

#
# Excepted format for the .gitmodules file:
# [submodule "meta-genivi-dev"]
#    path = meta-genivi-dev
#    url = http://github.com/genivi/meta-genivi-dev.git

# Ref to the github URL
github_url = "tldlab23.tl.intel.com" #"github.forestscribe.intel.com"
github_url = "gitlab.forestscribe.intel.com"
organization = "forestscribe-android"
input_file = "list_project_path_names.txt"

token_tldlab23 = "Ws6qyNwFo5Racz-jWvQC"
token_gitlab_marathon = "eLzF-u6Pjmy-hFzUyZck"

print "set -x"

#os.system('repo list > {}'.format(input_file))
for line in open(input_file, "r"):
    line = line.strip()
    (path, name) = line.split(' : ')
    name = re.sub('/','_', name)
    cmd = ""

    # To generate the script that will create all the repos
    if 0:
        cmd += "curl --header \"PRIVATE-TOKEN: {}\" -X POST \"https://{}/api/v3/projects?name={}&visibility=public&namespace_id=11\"".format(token_gitlab_marathon, github_url, name)
        print cmd

    if 0:
        print "git submodule add -f git@github.forestscribe.intel.com:forestscribe-android/{}.git {}".format(name, path)

    # To push on github
    if 1:
        cmd = "cd {}\n".format(path)
        #cmd += "export GIT_SSL_NO_VERIFY=1"
        cmd += "git fetch --unshallow\n"
        cmd += "git branch -D master; git checkout origin/HEAD -b master\n"
        cmd += "git push https://mickaelm:mickaelm@{}/{}/{} master\n".format(github_url, organization, name)
        cmd += "cd -\n"
        print cmd

    # To generate the script that will create all the repos
    if 0:
        r = requests.post('http://{}/api/v3/orgs/{}/repos'.format(github_url, organization),
                data=json.dumps({'name':name}),
                verify=False)
        print r
