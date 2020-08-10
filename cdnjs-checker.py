# This work is licensed under a Creative Commons Attribution-ShareAlike 4.0 International License.
# https://creativecommons.org/licenses/by-sa/4.0/

# Author: newtovaux
# https://github.com/newtovaux/cdn-js-checker

import urllib.request
import sys
import re
import os.path
import json
from packaging import version

re_http_test = r"http"
re_cdnjs_test = r"(?P<cdnjsurl>https?:\/\/cdnjs\.cloudflare\.com\/ajax\/libs\/(?P<library>[-a-zA-Z0-9@:%._\+~#=]+)\/(?P<version>[-a-zA-Z0-9@:%._\+~#=]+)\/\S+)\""
cdnjsapi = "https://api.cdnjs.com/libraries/{lib}?fields=name,filename,version"
updates = 0
aheads = 0

###############################################################################
# Print usage

def usage():
    print("{file} URL|file".format(file = __file__))
    print("e.g.\n\t{file} https://www.cdnjs.com\n\tor\n\t{file} ./testfile.html".format(file = __file__))

    return

###############################################################################
# Function to call the cdnjs API and compare versions

def fnCheckLatest(library, used_ver):
    global updates, aheads
    url = cdnjsapi.format(lib = library)
    j = json.load(urllib.request.urlopen(url))
    api_ver = j['version']

    # Is the API default version more up to date than the used version?
    # Red
    if version.parse(used_ver) < version.parse(api_ver):
        print("\t\033[31mcdnjs default version available: {api_ver}\033[0m".format(api_ver = api_ver))
        updates += 1

    # Is the API default version the same as the used version?
    # Green
    if version.parse(used_ver) == version.parse(api_ver):
        print("\t\033[32mcdnjs default version available: {api_ver}\033[0m".format(api_ver = api_ver))

    # Is the API default version less up to date than the used version?
    # Yellow
    if version.parse(used_ver) > version.parse(api_ver):
        print("\t\033[33mcdnjs default version available: {api_ver}\033[0m".format(api_ver = api_ver))
        aheads += 1

    return

###############################################################################
# Function to parse the contents for cdnjs references

def fnParse(content):

    matches = re.finditer(re_cdnjs_test, content, re.MULTILINE)
    count = 0

    # Look at eqach match in the contents
    for matchNum, match in enumerate(matches, start=1):
        print()
        print("Found ({mn}): {match}".format(mn = matchNum, match = match.group()))

        # Check ther are group matches
        if match.groups():
            library = match.group('library')
            version = match.group('version')
            print("\tLibrary: {lib}\n\tVersion identified: {ver}".format(lib = library, ver = version))
            fnCheckLatest(library, version)
            count += 1

    if count == 0:
        sys.stderr.write("No use of cdnjs found.")
        sys.exit(1)

    global updates, aheads
    print("\n{count} update(s) available.".format(count = updates))
    print("{count} libraries ahead of the default version.\n".format(count = aheads))

    return

###############################################################################
# Test if you have a command line option

if len(sys.argv) != 2:
    sys.stderr.write("Error: No command line option supplied. At least one command line option is expected.\n")
    usage()
    sys.exit(1)

# Grab the command line option
cmo = sys.argv[1]

# What type of command line option was it?
if re.match(re_http_test, cmo):
    # Looks like a URL
    fp = urllib.request.urlopen(cmo)
    mybytes = fp.read().decode("ascii") 
    fnParse(mybytes)
    fp.close()
else:
    # Looks like a file, test it
    if os.path.exists(cmo) and os.path.isfile(cmo):
        try:
            cmo_file = open(cmo, 'r')
            fnParse(cmo_file.read())
            cmo_file.close()
        except IOError:
            sys.stderr.write("Error: Unable to open file.\n")
            sys.exit(1)
    else:
        sys.stderr.write("Error: File does not exist, or is not a file.\n")
        sys.exit(1)

sys.exit(0)
