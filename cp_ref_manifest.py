#!/usr/bin/env python

import argparse
import json
import os.path
import re
import shutil
import sys
import tempfile

from datetime import date
from datetime import datetime
from datetime import timedelta

# Constants
URL_ARTIFACTORY = "https://jfstor001.jf.intel.com/artifactory/cactus-absp-jf"

# functions


def CreateAndUploadReferenceManifestDir(builder, date_dir="", r1="", r2="", manifest="", url=""):

    # Create a temporary directory and switch to it
    dirpath = tempfile.mkdtemp()
    os.chdir(dirpath)

    if url != "":
        result = re.search("(.*/artifactory/[^/]+)/(.*)", url)
        if result is None:
            sys.exit("Wrong URL format : {}")
        server_url = result.group(1)
        url_dir = result.group(2)
        tar_root = url_dir

        print server_url, url_dir

        # Create the weekly directory
        if os.path.isdir(url_dir):
            shutil.rmtree(url_dir)
        os.makedirs(url_dir)

        if manifest == "":
            r1_dest = "{}/manifest-generated-r1.xml".format(url_dir)
            shutil.copy(r1, r1_dest)
            r2_dest = "{}/manifest-generated-r2.xml".format(url_dir)
            shutil.copy(r2, r2_dest)
            json_data = {"r1": "{}/{}".format(server_url, r1_dest),
                         "r2": "{}/{}".format(server_url, r2_dest)}
        else:
            manifest_dest = "{}/manifest-generated.xml".format(url_dir)
            shutil.copy(manifest, manifest_dest)
            json_data = {"{}".format(builder): "{}/{}".format(server_url, manifest_dest)}
        with open("{}/manifests-generated.json".format(url_dir), 'w') as fdest:
            json.dump(json_data, fdest)

        # Display result URL
        print "\nGo to the following URL to check the results:\n. {}/{}".\
            format(server_url, url_dir)

    else:
        # Get the current date
        today = datetime.now()

        # Define the different date parameters
        if date_dir == "":
            # Take the previous day
            date_dir = today - timedelta(days=1)
            # Need to switch to the previous working week
            if today.strftime("%W") == date_dir.strftime("%W"):
                date_dir = today - timedelta(days=7)
        else:
            day = int(date_dir[0:2])
            if day not in range(1, 31 + 1):
                sys.exit("The day {} of the specified date {} is not between 1 and 31 (reminder: "
                         "expected format DDMMYYY)".format(day, date_dir))
            month = int(date_dir[2:4])
            if month not in range(1, 12 + 1):
                sys.exit("The month {} of the specified date {} is not between 1 and 12 (reminder: "
                         "expected format DDMMYYY)".format(month, date_dir))
            year = int(date_dir[4:])
            year_today = int(today.strftime("%Y"))
            if year not in range(2015, year_today + 1):
                sys.exit("The year {} of the specified date {} is not between {} and {} (reminder: "
                         "expected format DDMMYYY)".format(year, date_dir, 2015, year_today))
            date_dir = date(year, month, day)

        year = int(date_dir.strftime("%Y"))
        week = "{:02d}".format(int(date_dir.strftime("%W")))
        day = "{:02d}".format(int(date_dir.strftime("%d")))
        month = "{:02d}".format(int(date_dir.strftime("%m")))

        # Define the weekly directory
        weekly_dir = "build/eng-builds/{}/PSI/weekly/{}_WW{}/check".format(builder, year, week)

        # Create the weekly directory
        if os.path.isdir(weekly_dir):
            shutil.rmtree(weekly_dir)
        os.makedirs(weekly_dir)
        if manifest == "":
            r1_dest = "{}/manifest-initial-r1.xml".format(weekly_dir)
            shutil.copy(r1, r1_dest)
            r2_dest = "{}/manifest-initial-r2.xml".format(weekly_dir)
            shutil.copy(r2, r2_dest)
            json_data = {"r1": "{}/{}".format(URL_ARTIFACTORY, r1_dest),
                         "r2": "{}/{}".format(URL_ARTIFACTORY, r2_dest)}
        else:
            manifest_dest = "{}/manifest-initial.xml".format(weekly_dir)
            shutil.copy(manifest, manifest_dest)
            json_data = {"{}".format(builder): "{}/{}".format(URL_ARTIFACTORY, manifest_dest)}
        with open("{}/manifest-initial.json".format(weekly_dir), 'w') as fdest:
            json.dump(json_data, fdest)

        # Define the directory directory
        daily_dir = "build/eng-builds/{}/PSI/daily/{}{}{}_0000".format(builder, year, month, day)

        # Create the daily directory
        if os.path.isdir(daily_dir):
            shutil.rmtree(daily_dir)
        os.makedirs(daily_dir)
        if manifest == "":
            r1_dest = "{}/manifest-initial-r1.xml".format(daily_dir)
            shutil.copy(r1, r1_dest)
            r2_dest = "{}/manifest-initial-r2.xml".format(daily_dir)
            shutil.copy(r2, r2_dest)
            json_data = {"r1": "{}/{}".format(URL_ARTIFACTORY, r1_dest),
                         "r2": "{}/{}".format(URL_ARTIFACTORY, r2_dest)}
        else:
            manifest_dest = "{}/manifest-initial.xml".format(daily_dir)
            shutil.copy(manifest, manifest_dest)
            json_data = {"{}".format(builder): "{}/{}".format(URL_ARTIFACTORY, manifest_dest)}
        with open("{}/manifest-initial.json".format(daily_dir), 'w') as fdest:
            json.dump(json_data, fdest)

        # Display result URL
        print "\nGo to the following URLs to check the results:\n. {}/{}\n. {}/{}\n".\
            format(URL_ARTIFACTORY, daily_dir, URL_ARTIFACTORY, weekly_dir)

        server_url = URL_ARTIFACTORY
        tar_root = "build"

    # Tar the build directory
    tar_file = "build.tar"
    os.system('tar cf {} {}'.format(tar_file, tar_root))

    # Upload the tar file
    os.system('curl --header "X-Explode-Archive: true" --upload-file {} {}/'.
              format(tar_file, server_url))

    # Delete the temporary directory
    shutil.rmtree(dirpath)

#
# main function
#

# Parse the parameters
parser = argparse.ArgumentParser(description='''
With the manifests specified in parameters the script will prepare the directory structure.
And upload the whole stuff into {} server.
To be used during https://wiki.ith.intel.com/display/CACTUS/Create+a+new+BUILDBOT+builder steps.
    '''.format(URL_ARTIFACTORY))
parser.add_argument("--r1", help="specify the r1 manifest",
                    required=False, type=str, default="")
parser.add_argument("--r2", help="specify the r2 manifest",
                    required=False, type=str, default="")
parser.add_argument("--manifest", help="specify the manifest",
                    required=False, type=str, default="")
parser.add_argument("--builder", help="specify the buildbot builder",
                    required=False, type=str, default="")
parser.add_argument("--date", help="specify the date (format DDMMYYYY)",
                    required=False, type=str, default="")
parser.add_argument("--artifactory_url", help="specify the Artifactory URL",
                    required=False, type=str, default="")


# check the parameters
args = parser.parse_args()
if args.r1 != "":
    # check that the file exists
    if not os.path.isfile(args.r1):
        sys.exit("The file {} does not exist".format(args.r1))
    if args.r2 == "":
        sys.exit("the parameter r1 is defined but not r2")
    elif not os.path.isfile(args.r2):
        sys.exit("The file {} does not exist".format(args.r2))
else:
    if args.r2 != "":
        sys.exit("the parameter r2 is defined but not r1")
    else:
        if args.manifest != "":
            if not os.path.isfile(args.manifest):
                sys.exit("The file {} does not exist".format(args.manifest))
        else:
            sys.exit("At least manifest or r1 / r2 parameters should be specified")

# Create the weekly and daily directories and upload them on Artifactory
CreateAndUploadReferenceManifestDir(args.builder,
                                    date_dir=args.date,
                                    r1=args.r1,
                                    r2=args.r2,
                                    manifest=args.manifest,
                                    url=args.artifactory_url)
