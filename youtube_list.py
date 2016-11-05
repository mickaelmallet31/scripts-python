import re
import sys
import subprocess

# ------------------------------------
def execute(start, stop, name):
# ------------------------------------
	cmd = "ffmpeg -i '" + sys.argv[1] + "' -ss " + start
	if stop != "":
		cmd += " -to " + stop
	cmd += " '" + name + ".mp3'"
	print "Execution of command : " + cmd
	subprocess.call(cmd, shell=True)

# ------------------------------------
def format_2():
# ------------------------------------
        f = open(sys.argv[2], "r")
        counter = 0
	start_prev = ""
	name_prev = ""
        for line in f:
                counter += 1
		result = re.search("(.+) ([0-9]*:*[0-9]+:[0-9]{2}) *- *([0-9]*:*[0-9]+:[0-9]{2})", line)
		if result:
			name = "%02d - %s" % (counter, result.group(1))
			start = result.group(2)
			stop = result.group(3)
			if start_prev != "":
				execute(start_prev, start, name_prev)
				start_prev = ""
			execute(start, stop, name)
		else:
		        result = re.search("([0-9]*:*[0-9]+:[0-9]{2}) *- *(.+)", line)
		        if result:
		                name = "%02d - %s" % (counter, result.group(2))
		                start = result.group(1)
				if start_prev != "":
					execute(start_prev, start, name_prev)
				start_prev = start
				name_prev = name
	if start_prev != "":
        	execute(start_prev, "", name_prev)

# ------------------------------------
# main
# ------------------------------------
format_2()

