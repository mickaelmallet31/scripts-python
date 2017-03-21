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
input_file = "list_project_path_names.txt"

#os.system('repo list > {}'.format(input_file))
for line in open(input_file, "r"):
    line = line.strip()
    (path, name) = line.split(' : ')
    name = re.sub('/','_', name)

    # To generate the gitmodules file
    #print "[submodule \"{}\"]\n\tpath = {}\n\turl = http://github.com/genivi/{}.git\n".format(path, path, name)

    # To generate the script that will create all the repos
    r = requests.post('https://github.forestscribe.intel.com/api/v3/orgs/forestscribe-android/repos', 
            data=json.dumps({'name':name}),
            verify=False)
    print r

