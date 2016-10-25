#!/usr/bin/env python

import argparse
import collections
import glob
import os
import re
import shlex
import shutil
import subprocess
import sys
import yaml


MAGE = '\033[95m'
BLUE = '\033[94m'
GREEN = '\033[92m'
RED = '\033[91m'
BOLD = '\033[1m'
REGULAR = '\033[0m'
UNDERLINE = '\033[4m'
dictOut = {}
GITFETPROD = "platform/buildbot/prod:remotes/origin/platform/buildbot/prod"
DEFAULTMURL1 = "ssh://android.intel.com/a/aosp/platform/manifest"
DEFAULTMURL2 = "ssh://android.intel.com/manifests"
HEL = "This script finds a specified expression in manifest"\
      " project across branches. In addition to standard output, a log file"\
      " is generated with the research result named 'search_result.log'."\
      " Example:\n"\
      "./find_in_branches.py -e manifests -f yaml -f xml -p ci_model -p hours\n"\
      ". See https://wiki.ith.intel.com/display/CACTUS/Tools#Tools-find_in_branches.py for details."


class Return2Value(object):

    def __init__(self, v0, v1):
        self.v0 = v0
        self.v1 = v1


class Tee(object):

    def __init__(self, *files):
        self.files = files

    def write(self, obj):
        for f in self.files:
            f.write(obj)
            f.flush()  # If you want the output to be visible immediately

    def flush(self):
        for f in self.files:
            f.flush()


def ExtractKeys(dict_in):
    global dictOut
    for key, value in dict_in.iteritems():
        if isinstance(value, dict):  # If value itself is dictionary
            ExtractKeys(value)
        else:
            dictOut.setdefault(key, value)


def ExtractOccurence(expression, parameters, fileCheck):
    exportedRef = {}
    if "/" in parameters[1]:
        destProject = parameters[1].split('/')[-1]
    else:
        destProject = parameters[1]
    cmd = "git clone -q {}".format(parameters[1])
    print "\t{}".format(cmd)
    if not os.path.isdir(destProject):
        subprocess.call(shlex.split(cmd))
    try:
        os.chdir(destProject)
    except:
        print "      {}>>> Exception in {}, "\
              "no manifest found <<<{}".format(RED, parameters[0], REGULAR)
        return Return2Value(exportedRef, "")
    cmd = "git checkout -q remotes/origin/{}".format(parameters[0])
    print "\t{}".format(cmd)
    subprocess.call(shlex.split(cmd))

    for root, dirs, files in os.walk("./"):
        for name in files:
            if name.endswith(fileCheck):
                fname = os.path.join(root, name)
                with open(fname) as myfile:
                    lineOccurences = {}
                    for num, line in enumerate(myfile, 1):
                        line = line.strip()
                        if expression[1] == 'large':
                            if re.search(expression[0], line.rstrip()):
                                lineOccurences[num] = line
                        elif expression[1] == 'restrict':
                            line_words = re.findall(r'[\w"]+', line.rstrip())
                            if list(set(line_words) &
                                    set(expression[0].split())):
                                lineOccurences[num] = line
                        else:
                            print "      {}>>> Exception , wrong expression"\
                                  " <<<{}".format(RED, REGULAR)
                    if lineOccurences != {}:
                        exportedRef[fname] = lineOccurences
                myfile.close()
    os.chdir("../")
    return Return2Value(exportedRef, destProject)


def ExtractBuilder(printParams, selParamsVal):
    global dictOut
    buildeTable = {}
    paramValues = {}
    dictOut = {}
    checkKeys = {}

    useDefUrl = False

    for filename in glob.glob("../../../yamls/android/branches/*.yaml"):
        filterPass = True
        useDefUrl = False
        builder_param = yaml.load(open(filename, "r"))
        dictOut = {}
        checkKeys = {}
        ExtractKeys(builder_param)
        paramValueBuilder = dictOut

        if printParams:
            for printParam in printParams:
                if printParam in paramValueBuilder.keys():
                    checkKeys.setdefault(printParam,
                                         paramValueBuilder.get(printParam))
                else:
                    checkKeys.setdefault(printParam, "Not Found")

        if selParamsVal:
            for p, v in selParamsVal.iteritems():
                if p not in paramValueBuilder.keys():
                    filterPass = False
                else:
                    if v != paramValueBuilder.get(p):
                        filterPass = False
        if filterPass and ('android_branches.yaml' in builder_param):
            local1 = builder_param.get('android_branches.yaml')
            local2 = local1.get(local1.keys()[0])
            manifestUrl = (local2.get('repo')).get('manifest_url')
            manifestBranch = (local2.get('repo')).get('manifest_branch')
            curr_builder = local1.keys()[0][9:]
            skipBuilder = False
            if manifestBranch is None:
                print "Error: Builder parameter not correct - Manifest branch",\
                      "missing, skipping {}.".format(curr_builder)
                skipBuilder = True
            elif manifestUrl is None:
                global_param = yaml.load(open("../../../yamls/android/global.yaml", "r"))
                defaulUrl = global_param.get('repourl')
                manifestUrl = DEFAULTMURL1
                if defaulUrl is None:
                    useDefUrl = raw_input(("Warning: Bad builder parameter" +
                                           " - Manifest URL missing. Use " +
                                           "default value instead {} for {}" +
                                           " y/N ?\n").format(DEFAULTMURL1,
                                                              curr_builder))
                    if useDefUrl == 'y':
                        manifestUrl = DEFAULTMURL1
                        skipBuilder = False
                    else:
                        skipBuilder = True
                else:
                    manifestUrl = defaulUrl
                    skipBuilder = False
            if not skipBuilder:
                if curr_builder not in buildeTable.keys():
                    buildeTable.setdefault(curr_builder, (manifestBranch,
                                                          manifestUrl))
                else:
                    print "Warning: Builder found twice", \
                          "processing {}.".format(curr_builder)
                    buildeTable[curr_builder].update(manifestBranch,
                                                     manifestUrl)
            paramValues.setdefault(curr_builder, checkKeys)

    buildeTable = collections.OrderedDict(sorted(buildeTable.items()))
    return Return2Value(buildeTable, paramValues)


def main(argv):
    # Setting outputs-----------------------------------------------------------
    global logFile
    logFile = open("search_result.log", 'w')
    # original = sys.stdout //To use stdout uncomment then sys.stdout = original
    sys.stdout = Tee(sys.stdout, logFile)
    output = {}
    # Setting default parameters------------------------------------------------
    expressionToFind = ''
    fileToCheck = 'yaml'
    builderToCheck = True
    printParams = []
    selParamsVal = {}
    # Parse the parameters------------------------------------------------------
    parser = argparse.ArgumentParser(description=HEL)

    parser.add_argument("-e", "--expression",
                        help="expression to find in all repo contents, use '' "
                        "if expression contains spaces or tabs",
                        required=False)

    parser.add_argument("-E", "--exactword",
                        help="exact a single word to find in all repo contents",
                        required=False)

    parser.add_argument("-a", "--all_branches",
                        help="if provided then research is done on "
                        "all references (Not functionnal)",
                        required=False,
                        default=False,
                        action='store_true')

    parser.add_argument("-f", "--file_type",
                        help="xml, yaml or py (default value: yaml) ."
                        "You can use more that one type, for that put "
                        " -f <type1> -f <type2> etc.",
                        required=False,
                        default=["yaml"],
                        action='append')

    parser.add_argument("-p", "--parameter",
                        help="Shows the provided parameter's value in the"
                        " builder's setting if found and prints 'not found'"
                        " otherwise. You can use more that one type, for"
                        " that put -p <param1> -p <param2> etc. Default value: ci_model",
                        required=False,
                        default=["ci_model"],
                        action='append')

    args = parser.parse_args()
    fileToChecks = args.file_type
    builderToCheck = not args.all_branches
    printParams = args.parameter
    printParamsNew = []
    selParamsVal = {}
    listRepo = []
    if args.expression:
        if args.exactword:
            print "{}Error: Use -e or -E, not both{}".format(RED, REGULAR)
            logFile.close()
            sys.exit(2)
        else:
            expressionToFind = (args.expression, 'large')
    else:
        if args.exactword:
            expressionToFind = (args.exactword, 'restrict')
        else:
            print "{}Error: No expression provided to seach{}".format(RED, REGULAR)
            logFile.close()
            sys.exit(2)

    if expressionToFind == '':
        print "{}Error: No expression provided to seach{}".format(RED, REGULAR)
        logFile.close()
        sys.exit(2)
    filetypes = ()
    for fileToCheck in fileToChecks:
        if fileToCheck not in ["yaml", "xml", "py"]:
            print"Warning: -f argument is not yaml, xml or py,",\
                 " picking 'yaml' by default"
        else:
            filetypes += (fileToCheck,)
    if not filetypes:
        fileToCheck = ("yaml",)
    if builderToCheck:  # Later enable builderToCheck check
        # Parsing all builders--------------------------------------------------
        print "Cloning config repo..."
        for elem in printParams:
            if ":" in elem:
                if elem.split(':')[0] not in selParamsVal.keys():
                    selParamsVal.setdefault(elem.split(':')[0],
                                            elem.split(':')[-1])
                    printParamsNew.append(elem.split(':')[0])
                else:
                    selParamsVal[elem.split(':')[0]] += [elem.split(':')[-1]]
            else:
                printParamsNew.append(elem)

        retval = ExtractBuilder(printParamsNew, selParamsVal)
        builderTable = retval.v0
        printedParams = retval.v1
        count = 1
        for builder, parameter in builderTable.iteritems():

            print "{}- {}/{}: builder '{}', {}, used manifest"\
                  " URL: {}{}".format(BLUE,
                                      count,
                                      len(builderTable.keys()), builder,
                                      parameter[0],
                                      parameter[1],
                                      REGULAR,
                                      )
            if printParams:
                for paramtoshow, value in printedParams[builder].iteritems():
                    if value != "Not Found":
                        color = MAGE
                    else:
                        color = BLUE
                    print "      Parameter {}: {}"\
                          "{}{}".format(paramtoshow, color, value, REGULAR)
            dummy = ExtractOccurence(expressionToFind,
                                     parameter,
                                     filetypes)
            if dummy.v0 != {}:
                output.update({str(parameter[0]): dummy.v0})
                print "      {}Found:{}".format(GREEN, REGULAR)
                for filename, lines in (dummy.v0).iteritems():
                    print "{}\t- '{}', lines:{}".format(GREEN, filename, REGULAR)
                    for num, line in lines.items():
                        print "\t\t{} - {}: {}{}".format(GREEN, num, line, REGULAR)
            else:
                print "      No occurences found"
            count += 1
            if dummy.v1 and (dummy.v1 not in listRepo):
                listRepo.append(dummy.v1)
        for repoManifest in listRepo:
            shutil.rmtree(repoManifest)
    else:
        # Parsing all references------------------------------------------------
        print(("IMPORTANT: Parsing all revisions on:\n\t- {}\n\t- " +
               "{}").format(DEFAULTMURL1, DEFAULTMURL2))
        for defurl in [DEFAULTMURL1, DEFAULTMURL2]:
            # listRevision = []
            subprocess.call(shlex.split("git clone -q " + defurl))
            if "/" in defurl:
                destProject = defurl.split('/')[-1]
            else:
                destProject = defurl
            os.chdir(destProject)
            listbranch_parse = open("listebranch", 'w+')
            subprocess.Popen(shlex.split("git branch -a"),
                             stdout=listbranch_parse)
            listbranch_parse.close()
            listbranch = open("listebranch", 'r')
            numberRevision = 1
            listreduced_parse = open("listereduced", "w+")
            for n, line in enumerate(listbranch):
                line = line.rstrip()
                print line
                if re.search("/release/", line):
                    listreduced_parse.write(line)
                    numberRevision += 1
            listreduced_parse.close()
            listbranch.close()
            os.chdir("../")
            shutil.rmtree(destProject)
    logFile.close()

if __name__ == "__main__":
    main(sys.argv[1:])
