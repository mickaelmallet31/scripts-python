#!/usr/bin/env python

""" See for more details https://wiki.ith.intel.com/display/CACTUS/Buildbot+master+clean+up """

#
# Imports
#
import os
import re

#
# Variable settings
#
# pickles directory
localDir = os.path.dirname(os.path.realpath(__file__))
picklesDir = "{}/../../../workdir/pickles".format(localDir)
# output files names
rootDir = "/tmp"
old_pickles = "{}/output.txt".format(rootDir)
builders_still_active = "{}/output_list_builders_minus_one_year.txt".format(rootDir)
dest = "{}/files_to_be_deleted.txt".format(rootDir)

# retention policy parameters
keep_pickles_newer_than = 365
keep_last_pickles_of_obsolete_builder = 5

# Determine the old pickles sorted by newest file first
os.system("cd {} && find * -type f -mtime +{} -printf '%T+ %p %k\n' | sort --reverse > {}".
          format(picklesDir, keep_pickles_newer_than, old_pickles))

# determine the builders still active since one year
os.system("cd {} && find * -maxdepth 1 -type f -mtime -{} | sed -e 's!\/[^/]*$!!' | sort -u > {}".
          format(picklesDir, keep_pickles_newer_than, builders_still_active))

# Get the list of active builders
table_builders_still_active = []
table_builders_inactive = {}
for line in open(builders_still_active):
    table_builders_still_active.append(line.strip())

# Open the destination file that will contain the list of pickles that are compliant with
# the retention parameters
fdest = open(dest, 'w')

# Init the total gain of disk space if all the selected pickles are deleted
total_gain = 0

# Read the old pickles input file
for line in open(old_pickles):
    line = line.strip()
    res = re.search('\s(.+)/(\d+) (.*)$', line)

    # skip the line if not formated correctly
    if res is None:
        continue

    metabuild = res.group(1)
    number = res.group(2)
    size = res.group(3)

    # If the build is in the builder still active then
    if metabuild in table_builders_still_active:
        # remove this pickle
        fdest.write('{}/{}\n'.format(metabuild, number))
        total_gain += int(size)
    else:
        # remove the pickle only if the quota of old pickles of obsolete builders is raised
        if metabuild not in table_builders_inactive:
            table_builders_inactive[metabuild] = 1
        else:
            table_builders_inactive[metabuild] = + 1

            if table_builders_inactive[metabuild] > keep_last_pickles_of_obsolete_builder:
                fdest.write('{}/{}\n'.format(metabuild, number))
                total_gain += int(size)
fdest.close()

print "List of pickles to be deleted present in '{}'".format(dest)
print "Expected disk space gain: {:,} Kb".format(total_gain)
print """
    Execute the following script to do the clean up:
    cd {}
    for file in `cat {}`
    do
        rm -rf $file
    done

""".format(picklesDir, dest)
