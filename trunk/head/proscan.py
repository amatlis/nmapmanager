#!/usr/bin/env python
# encoding: utf-8
"""
proscan.py

Created by Steven McGrath on 2009-05-14.
Copyright (c) 2009 GNU Public Licence.
"""

import sys
import getopt
import nmap

help_message = '''
This script is used for running profile nmap scans.  These scans are 
pre-written for use in the cron 

'''


class Usage(Exception):
  def __init__(self, msg):
    self.msg = msg


def main(argv=None):
  if argv is None:
    argv = sys.argv
  
  debug = False
  config_file = nmap.CONFIG
  taskname = "none"
  
  try:
    try:
      opts, args = getopt.getopt(argv[1:], "dht:c:", ["debug", "help", "task=", "config="])
    except getopt.error, msg:
      raise Usage(msg)
  
    # option processing
    for option, value in opts:
      if option == "-v":
        verbose = True
      if option in ("-h", "--help"):
        raise Usage(help_message)
      if option in ("-t", "--task"):
        taskname = value
      if option in ("-c", "--config"):
        config_file = value
      if option in ("-d", "--debug"):
        debug = True
  
  except Usage, err:
    print >> sys.stderr, sys.argv[0].split("/")[-1] + ": " + str(err.msg)
    print >> sys.stderr, "\t for help use --help"
    return 2

  config, scanners = nmap.load_config(config_file)
  
  if debug:
    config['debug'] = True
  
  for scanner in scanners:
    for task in scanner.tasks:
      if task.name.upper() == taskname.upper():
        nmap.run_scan(config, scanner, task)
  

if __name__ == "__main__":
  sys.exit(main())
