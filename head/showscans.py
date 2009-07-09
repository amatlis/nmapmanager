#!/usr/bin/env python
# encoding: utf-8
"""
nmap_cfg.py

Created by Steven McGrath on 2009-05-14.
Copyright (c) 2009 GNU Public Licence.
"""

import sys
import getopt
import nmap

help_message = '''
The help message goes here.
'''


class Usage(Exception):
  def __init__(self, msg):
    self.msg = msg


def main(argv=None):
  if argv is None:
    argv = sys.argv
  try:
    try:
      opts, args = getopt.getopt(argv[1:], "hH", ["header","help"])
    except getopt.error, msg:
      raise Usage(msg)
  
    # option processing
    
    header = False
    for option, value in opts:
      if option in ("-h", "--help"):
        raise Usage(help_message)
      if option in ("-H", "--header"):
        header = True
  
  except Usage, err:
    print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
    print >> sys.stderr, "\t for help use --help"
    return 2
  
  config, scanners = nmap.load_config(nmap.CONFIG)
  
  output = []
  for scanner in scanners:
    for task in scanner.tasks:
      output.append(' %5s %-20s %-20s' % (task.time, task.name, task.ip_range))
      
  output.sort()
  
  if header:
    print " Time       Scan Name            IP Range"
    print " ----- -------------------- --------------------"

  for item in output:
    print item

if __name__ == "__main__":
  sys.exit(main())
