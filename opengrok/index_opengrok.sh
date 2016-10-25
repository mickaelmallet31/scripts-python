#!/bin/bash

source ~/.bashrc

# variables harcoded in  /usr/opengrok/bin/OpenGrok
 #export OPENGROK_VERBOSE=true;
 #export IGNORE_PATTERNS="-i *.bin -i prebuilts";
 #export OPENGROK_SCAN_DEPTH="10";

REPO=${HOME}/bin/repo
DIR=/data/src
LOG_FILE=${DIR}/index_opengrok.log
fileAll=${DIR}/listALL.txt
fileRestricted=${DIR}/listRESTRICTED.txt
fileSync=${DIR}/listSYNC.txt
attached_file=${DIR}/log_file_`date '+%Y%m%d_%H%M%S'`.tar.gz
src_dir=`dirname $0`
opengrok_conf_file=$src_dir/opengrok.conf
email_file=${DIR}/email.txt
lock_file=${DIR}/lock_file.txt

# Check that there is no on going execution
if [ -f $lock_file ]; then
    echo "Opengrok execution on going ($lock_file present)"
    exit 1
fi
touch $lock_file

function sync_repo
{
    folder=$1
    project=$2
    branch=$3
    manifest=$4

    dir=$DIR/$folder
    fileAll=${dir}/listALL.txt
    fileRestricted=${dir}/listRESTRICTED.txt
    fileSync=${dir}/listSYNC.txt


    (
        echo "**** START REPO SYNC of $folder ****"
        date
        set -x

        mkdir -p $dir
        cd $dir
        $REPO init -u ssh://android.intel.com/$project -b $branch -m $manifest
        # repo sync done to recover the project.list file
        $REPO sync $project
        cd .repo/manifests

        # The restriction at AOSP level is done through the apache configuration file /etc/apache2/sites-available/ssl.conf
        git grep "<project " |grep "restricted=" | grep -v 'restricted="aosp"' | sed -e 's/.*path="//' -e 's/".*//' |sort -u > $fileRestricted
        sort -u ../project.list > $fileAll

        echo "Listing ALL projects vs RESTRICTED projects count..."
        wc $fileAll $fileRestricted

        comm -2 -3 $fileAll $fileRestricted > $fileSync

        echo "repo sync of project from $fileSync ..."
        cd -
        $REPO sync -j 5 `cat $fileSync`
        set +x
        $REPO manifest -r -o manifest_$folder.xml
        rm -rf `cat $fileRestricted`

        echo "**** END REPO SYNC of $folder ****"
        date
    ) |& tee -a $LOG_FILE
}

cd $DIR
rm -rf $LOG_FILE $attached_file

# Log the start date/time
(
set -x

echo "**** START date/time ****"
date
) |& tee -a $LOG_FILE

# *** BUILDBOT **********************************
sync_repo "BUILDBOT_PROD" "a/buildbot/manifests" "platform/buildbot/prod" "buildbot-prod"
sync_repo "BUILDBOT_STAGING" "a/buildbot/manifests" "platform/buildbot/staging" "buildbot-staging"
sync_repo "BUILDBOT_MAIN" "a/buildbot/manifests" "platform/buildbot/main" "buildbot-main"
sync_repo "WEBAPPS_MAIN" "a/buildbot/manifests" "platform/buildbot/main" "webapps"

# *** r51 ***************************************
sync_repo "CHT51_STABLE" "a/aosp/platform/manifest" "platform/android/cht51-stable" "android-cht51"

# *** 1A-L ***************************************
sync_repo "OneAndroid-L-MR1-CHT-R1" "manifests" "android/l/mr1/stable/cht/master" "r1"
sync_repo "OneAndroid-L-MR1-CHT-R2" "manifests" "android/l/mr1/stable/cht/master" "r2"

# *** 1A-M ***************************************
sync_repo "OneAndroid-M-MR1_ICE17" "manifests" "integ/mmr1_ice17" "ice17"
sync_repo "OneAndroid-M-MR1_SF3GR-MAINT" "manifests" "android/m/mr1/stable/sf3gr_maint/master" "sf3gr_maint"
sync_repo "OneAndroid-M-MR1_SofiaLTE_Quant" "manifests" "android/m/mr1/stable/sf_lte_q/master" "sf_lte_q"
sync_repo "OneAndroid-M-Stable-R2" "manifests" "android/m/mr1/stable/master" "r2"
sync_repo "R6_APACHE" "a/aosp/platform/manifest" "cas/platform/android/r6apache" "android-r6apache"
sync_repo "R6_INAK" "a/aosp/platform/manifest" "cas/platform/android/r6inak" "android-r6inak"
sync_repo "R6_LEGACY_R1" "a/aosp/platform/manifest" "platform/android/r6_legacy" "r1"
sync_repo "R6_LEGACY_R2" "a/aosp/platform/manifest" "platform/android/r6_legacy" "r2"
sync_repo "R61_STABLE" "a/aosp/platform/manifest" "cas/platform/android/r61_stable" "android-r61_stable"

# *** 1A-N ***************************************
sync_repo "N_CAR" "manifests" "android/master" "car"
sync_repo "OneAndroid-N-R0" "manifests" "android/master" "r0"
sync_repo "OneAndroid-N-R2" "manifests" "android/master" "r2"
sync_repo "Spartan_R0" "manifests" "cas/android/main" "r0"
sync_repo "Spartan_R1" "manifests" "cas/android/main" "r1"

# *** YOCTO **************************************
sync_repo "YOCTO" "a/yocto/manifest" "master" "default.xml"

(
time OPENGROK_CONFIGURATION=$opengrok_conf_file /usr/opengrok/bin/OpenGrok update

echo "**** FINISH date/time ****"
date
) |& tee -a $LOG_FILE


/bin/tar -czvf $attached_file $LOG_FILE `find -maxdepth 2 -name "manifest_*.xml"`

echo "
The 'repo sync' and OpenGrok index logs are available at ${attached_file}.

The SCRIPT/CRONTAB launching this email:
$(crontab -l)

For more data go to https://wiki.ith.intel.com/display/CACTUS/OpenGrok+Maintenance

The last 100 lines of $LOG_FILE:
======================================================================
" > $email_file
tail -20 $LOG_FILE >> $email_file

/usr/bin/mutt -s "cactus-source Opengrok: daily index log" -- cactus-infrastructure@intel.com < $email_file

# Remove the lock file
rm -rf $lock_file

# Delete the oldest log files
find ${DIR} -ctime +5 -name "log_file_*" -exec rm {} \;
