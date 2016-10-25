#!/usr/bin/env python

import os.path
import re
import shutil
import sys

#
# Read the soc information
#
repo_soc = {}
fs = open(sys.argv[1])
# Read the soc table
firstline = fs.readline().strip()
soc_table = firstline.split(",")
soc_table.pop(0)
# Read the list of soc per repo
for line in fs:
    table = line.strip().split(",")
    repo = table[0]
    table.pop(0)
    counter = 0
    list_soc = []
    for soc in table:
        if soc != "":
            list_soc.append(soc_table[counter])
        counter += 1
    if list_soc:
        repo_soc[repo] = {'soc': list_soc, 'treated': False}
#
# Looks for the repos in the files listed below
#
files_to_be_updated = [
    "include/bsp.xml",
    "include/bsp-priv.xml",
    "include/imc.xml",
    "include/imc-priv.xml",
]
for file_to_be_updated in files_to_be_updated:
    # Skip the file if not found
    if not os.path.isfile(file_to_be_updated):
        continue

    # Read the manifest file
    fd_filename = "{}.new".format(file_to_be_updated)
    fd = open(fd_filename, "w")
    for line in open(file_to_be_updated):
        for repo in repo_soc:
            value = repo_soc[repo]

            # For repo not treated yet
            if value['treated'] is False:

                # Looks for the repo in the project line
                if re.search('<project.* name="{}"'.format(repo), line):
                    # Found it
                    new_group_list = value['soc']

                    # Treat the line with groups
                    res = re.search('^(.*) groups="([^"]*)"(.*)', line)
                    if res is not None:
                        # groups found in the line
                        prefix = res.group(1)
                        group_list = res.group(2).split(",")
                        suffix = res.group(3)
                        regex = re.compile(r'soc_.*')
                        new_group_list.extend([i for i in group_list if not regex.search(i)])
                        line = '{} groups="{}"{}\n'.format(prefix, ','.join(sorted(new_group_list)), suffix)
                    else:
                        # groups not found in the line
                        res = re.search('^(.* name="[^"]*")(.*)', line)
                        line = '{} groups="{}"{}\n'.format(res.group(1), ','.join(sorted(new_group_list)), res.group(2))
                    repo_soc[repo]['treated'] = True

        # Print the line
        fd.write("{}".format(line))
    fd.close()

    # Override the src file by the dest file
    shutil.copyfile(fd_filename, file_to_be_updated)
    os.remove(fd_filename)

# Check that all the repo defined with soc are found
print "\nWARNING:\nList of repos not found in {}.\nPlease double check if this is normal:".format(files_to_be_updated)
for repo in sorted(repo_soc):
    if repo_soc[repo]['treated'] is False:
        print "\t- {}".format(repo)
