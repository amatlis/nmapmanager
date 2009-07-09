#!/usr/bin/env python
# encoding: utf-8
"""
nmap_cron.py

Created by Steven McGrath on 2009-05-13.
Copyright (c) 2009 GNU Public Licence.
"""

import sys
import os
import datetime
import nmap

def main():
  config, scanners = nmap.load_config(nmap.CONFIG)
  time = datetime.date.today().strftime('%H:%M')
  
  if time == "00:00":
    generate_report(scanners)
  
  for sensor in sensors:
    for task in sensor.tasks:
      if task.time == time:
        run_scan(config, scanner, task)

if __name__ == '__main__':
  main()

