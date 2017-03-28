#!/usr/bin/env python
# -*- coding: latin-1 -*-

import os
import re
from os import listdir
from os.path import isfile, join

# ========================================================================
# Functions
# ========================================================================

currentDir = os.getcwd()
onlyfiles = [f for f in listdir(currentDir) if isfile(join(currentDir, f))]

for filename in onlyfiles:
    res = re.search('(.*)\.([^\.]+)$', filename)
    if res is None:
        continue
    print filename
    file_wo_ext = res.group(1)
    ext = res.group(2)
    if ext != 'mp3':
        cmd = 'avconv -i "{}" "{}.mp3"'.format(filename, file_wo_ext)
        print ">>> {}".format(cmd)
        os.system(cmd)

