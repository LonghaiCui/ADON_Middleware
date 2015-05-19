#!/usr/local/bin/python
#Usage: python AdonClent.py filename
#e.g.:  python AdonClent.py xyz.img
import subprocess
import xmlrpclib
import sys

file = sys.argv[1]
proxy = xmlrpclib.ServerProxy("http://localhost:8888/")
print proxy.add_task('A', 1, 3)
p = subprocess.Popen([r'./iput','-v',file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output = p.communicate()
print output

