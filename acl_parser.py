#!/usr/bin/env python

import collections
import getopt
import os
import pip
import re
import shlex
import shutil
import subprocess
import sys

MAGE = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
RED = '\033[91m'
BOLD = '\033[1m'
REGULAR = '\033[0m'
UNDERLINE = '\033[4m'

GITFETCHARGS = "origin refs/meta/config:refs/remotes/origin/meta/config"
STDOUT = "&> /dev/null"
SEPARATOR = "\n-------------------------------------------------------\n"


def Help(val):
    print "\nsyntax :"
    print "--------"
    print "This script has several roles"
    print "1- It allows getting groups and permission settings for all refs" \
          " on a given repo project"
    print "./acl_parser.py -r <RepoProject> -p <permission> -d <display_type>\n"
    print "<RepoProject> : repo name on gerrit (All-Projects)"
    print "<permission>: gerrit permission : read, push, rebase, etc."
    print "<display_type>: "
    print "\t- cluster: This option provides set of references sharing"\
          " the exact setting for the given permission"\
          " i.e. gathering references together if they share the exact set of "\
          "attributes (Exclusive, forced etc.) for the given permission"
    print "\t- list: This option parses and prints for each reference the list"\
          " of groups provided for that permission"
    print "\t- tree: Provides raw output (prints the dict)\n"
    print "2- It allows aligning acl setting between 2 repo projects on a " \
          " given permission (for now it only works on read and exclusive " \
          " will automatically be set). This alignement will be done on all" \
          " revision on <RepoProject> that are non in <DestProject> "
    print "./acl_parser.py -r <RepoProject> -p <permission> -d update" \
          " -a <DestProject> -j <JIRA_for_new_patch>"
    print "<DestProject> : destination repo name on gerrit"
    print "<JIRA_for_new_patch>: CACTUS jira url, default value 'No-Jira'"

    if val == 1:
        InstPack = pip.get_installed_distributions()
        InstPackList = sorted(["{} - Version:{}".format(i.key, i.version)
                               for i in InstPack])
        print "Installed python packages :\n---------------------------"
        for elem in InstPackList:
            print "\t-  {}".format(elem)


def DisplayTree(output, p, destProject, jira):
    os.chdir("../")
    print "Display tree (raw values)\n"
    for r, groups in output.iteritems():
        print "{} :  {}".format(r, output[r])


def DisplayCluster(output, p, destProject, jira):
    os.chdir("../")
    print "Display clusters\n"
    cluster = {}
    for r, values in output.iteritems():
        SigLine = output[r][1]["Groups"]
        for k in range(0, len(output[r][0]["Attributes"])):
            SigLine += ["* Attr-" + output[r][0]["Attributes"][k]]
        SigLine.sort()
        sig = ','.join(str(val) for val in SigLine)
        if sig not in cluster.keys():
            cluster.setdefault(sig, [r])
        else:
            cluster[sig].append(r)
    for dummy, references in cluster.iteritems():
        print "--------------------------------\n {} :\n".format(p)
        attributes = []
        groups = []
        g = dummy.split(',')
        for elem in g:
            if elem.startswith("* Attr-"):
                attributes.append(elem.split("* Attr-")[-1])
            else:
                groups.append(elem)
        if attributes == []:
            print "\t", MAGE, "Attributes :", REGULAR, " No specific attributes"
        else:
            print "\t", MAGE, "Attributes :", REGULAR,\
                  " {}".format(','.join(str(v) for v in attributes))
        print "\t", MAGE, "Groups :", REGULAR
        for elem in groups:
            print "\t\t-  {}".format(elem)
        print BLUE, "\tReferences with the exact same setting :", REGULAR
        for elem in cluster[dummy]:
            print "\t\t-  {}".format(elem)


def DisplayList(output, p, destProject, jira):
    os.chdir("../")
    print "Display list\n"
    for r, values in output.iteritems():
        AttributeLine = ""
        for k in range(0, len(output[r][0]["Attributes"])):
            AttributeLine += output[r][0]["Attributes"][k]
        print "{} :  Attributes: {}".format(r, AttributeLine)
        print " " * (len(r) + 1) + \
              ":  Groups: {}".format(output[r][1]["Groups"])


def AlignProject(output, p, destProject, jira):
    exportedRef = []
    if not destProject:
        print "Error: Cannot align without destination project"
        Help(0)
        sys.exit(2)
    if p == "read":
        print "Transferring {} permission to {} " \
              " on all found references\n".format(p, destProject)
    else:
        print "Transferring {} permission to {} " \
              " is not possible, only read has this feature" \
              .format(p, destProject)
        sys.exit(2)
    os.chdir("../")
    folders = [folder for folder in os.listdir('.') if os.path.isdir(folder)]
    if "/" in destProject:
        valDest = str(destProject.split('/')[-1])
    else:
        valDest = destProject
    if valDest in folders:
        shutil.rmtree(valDest)
    os.makedirs(valDest)
    subprocess.call(shlex.split("git clone -q ssh://android.intel.com:29418/" +
                                destProject))
    os.chdir(valDest)
    subprocess.call(shlex.split("git fetch -q " + GITFETCHARGS))
    subprocess.call(shlex.split("git checkout -q meta/config"))
    outputDest = ExtractAclStruct(p)
    listGroups = outputDest.get("refs/*", False)
    groupSection = ""
    if not listGroups:
        print "Error: {} not set in refs/* settings".format(p)
    else:
        if "Exclusive" in listGroups[0]["Attributes"]:
            groupSection = "\texclusiveGroupPermissions = {}\n".format(p)
        for elem in listGroups[1]["Groups"]:
            if elem[0] != '':
                groupSection += "\t{} = {} group {}\n".format(p, elem[0],
                                                              elem[1])
            else:
                groupSection += "\t{} = group {}\n".format(p, elem[1])
        print "Adding below sections:\n{}".format(groupSection)
        for r in output.keys():
            if r not in outputDest.keys():
                exportedRef.append(r)
        pConfig = open("project.config", "a")
        for newRef in exportedRef:
            startRefSection = '[access "{}"]\n'.format(newRef)
            pConfig.write(startRefSection)
            pConfig.write(groupSection)
        pConfig.close()
        subprocess.call(shlex.split("git add project.config"))
        subprocess.call(shlex.split("scp -p -P 29418 android.intel.com"
                                    ":hooks/commit-msg .git/hooks/"))
        subprocess.call(shlex.split("git commit -sm ' "
                                    "Align acl settings: {}'".format(jira)))
        subprocess.call(shlex.split("git push origin "
                                    "HEAD:refs/for/refs/meta/config"))
        print "Patch generated:", GREEN, "OK", REGULAR, SEPARATOR
    os.chdir("../")
    shutil.rmtree(valDest)


def ExtractAclStruct(permission):
    output = {}
    regexp1 = "\s+exclusiveGroupPermissions\s+=\s+"
    regexp2 = "\s+" + permission + "\s+=\s+"
    with open("project.config") as acl:
        for line in acl:
            if line.startswith('[access "'):
                ref = line.split('"')[1]
                attributes = ()
            elif re.search(regexp1, line) and permission in line:
                attributes += ("Exclusive",)
            elif re.search(regexp2, line):
                try:
                    valGroup = (line.split("group")[-1]).rstrip()
                    if line.split()[2] == "group":
                        dummy = ('', valGroup)
                    else:
                        dummy = (line.split()[2], valGroup)
                    if ref not in output.keys():
                        output.setdefault(ref, ({"Attributes": attributes},
                                                {"Groups": [dummy]}))
                    else:
                        output[ref][1]["Groups"].append(dummy)
                except IndexError:
                    print "Error: acl file corrupted, no group found"
        output = collections.OrderedDict(sorted(output.items()))
    return output


def main(argv):
    output = {}
    RepoProject = ''
    DestProject = ''
    permission = ''
    DisplayType = ''
    JiraRef = 'No-Jira'

    DisplayFunctions = {'tree': DisplayTree,
                        'cluster': DisplayCluster,
                        'list': DisplayList,
                        'update': AlignProject,
                        '': DisplayList,
                        }

    AllowedDisplays = {"tree", "cluster", "list", "update", ""}
    try:
        opts, args = getopt.getopt(argv,
                                   "Hhr:p:d:a:j:",
                                   ["repo=", "permission=", "DisplayType="])
    except getopt.GetoptError:
        print "Error: Parameter missing"
        Help(0)
        sys.exit(2)
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            Help(0)
            sys.exit()
        elif opt in ("-H", "--Help"):
            Help(1)
            sys.exit()
        elif opt in ("-d", "--display-type"):
            if arg in AllowedDisplays:
                DisplayType = arg
            else:
                print "Parameters incorrect :"
                print 'Display type must be one of these', AllowedDisplays
                sys.exit(2)
        elif opt in ("-r", "--repo"):
            RepoProject = arg
        elif opt in ("-p", "--permission"):
            permission = arg
        elif opt in ("-a", "--align"):
            DestProject = arg
        elif opt in ("-j", "--jira"):
            JiraRef = arg
    if RepoProject == '' or permission == '':
        print RED, "Error: ", REGULAR, "Parameters missing :"
        Help(0)
        sys.exit(2)
    print "Parameters check:", GREEN, "OK", REGULAR, SEPARATOR
    folders = [folder for folder in os.listdir('.') if os.path.isdir(folder)]
    if "/" in RepoProject:
        shortRepoName = RepoProject.split('/')[-1]
    else:
        shortRepoName = RepoProject
    if shortRepoName in folders:
        shutil.rmtree(shortRepoName)
    os.makedirs(shortRepoName)
    subprocess.call(shlex.split("git clone -q ssh://android.intel.com:29418/" +
                                RepoProject))
    os.chdir(shortRepoName)
    subprocess.call(shlex.split("git fetch -q " + GITFETCHARGS))
    subprocess.call(shlex.split("git checkout -q meta/config"))
    output = ExtractAclStruct(permission)
    print "Extracting acl data from source Project",\
          GREEN, "OK", REGULAR, SEPARATOR
    DisplayFunctions[DisplayType](output, permission, DestProject, JiraRef)
    shutil.rmtree(shortRepoName)

if __name__ == "__main__":
    main(sys.argv[1:])
