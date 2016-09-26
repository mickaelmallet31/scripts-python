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
	res = re.search('(.*)\.[^\.]+', filename)
	file_wo_ext = res.group(1)
	cmd = 'avconv -i "{}" "{}.mp3"'.format(filename, file_wo_ext)
	print ">>> {}".format(cmd)
	os.system(cmd)

