#!/usr/bin/env python

from zenmapCore import NmapParser
from zenmapCore import NmapCommand
from config import Configuration
import ConfigParser
import os
import sys
import time
import calendar
import hashlib
import commands

class Scheduler(object):
  days_of_week    = range(0,7)
  weeks_of_month  = range(0,6)
  time_of_day     = []
  calendar_days   = range(1,32)
  recurring       = False
  flag            = False
  
  dow_dict        = {'sun': 0,
                     'mon': 1,
                     'tue': 2,
                     'wed': 3,
                     'thu': 4,
                     'fri': 5,
                     'sat': 6,
                         0: 'sun',
                         1: 'mon',
                         2: 'tue',
                         3: 'wed',
                         4: 'thu',
                         5: 'fri',
                         6: 'sat'
                    }
  
  def __init__(self):
    pass
  
  def set_schedule(**options):
    if 'days_of_week' in options:
      self.days_of_week   = options['days_of_week']
    if 'weeks_of_month' in options:
      self.weeks_of_month = options['weeks_of_month']
    if 'time_of_day' in options:
      self.time_of_day    = options['time_of_day']
    if 'calendar_days' in options:
      self.calendar_days  = options['calendar_days']
    if 'recurring' in options:
      self.recurring      = options['recurring']
  
  def check(self):
    if self.flag:
      return True
    else:
      ctime = self._get_current_time()
      if ctime['day_of_week'] in self.days_of_week:
        if ctime['week_of_month'] in self.weeks_of_month:
          if ctime['ftime'] in self.time_of_day:
            if ctime['date'] in self.calendar_days:
              self.check = True
              return True
      return False
    
  def parse_schedule(self, config):
    for option in config.options('Schedule'):
      if option == 'days of the week':
        self.days_of_week = clist(config, 'Schedule', option, rtype='int')
      elif option == 'weeks of the month':
        self.weeks_of_month = clist(config, 'Schedule', option, rtype='int')
      elif option == 'calendar days':
        self.calendar_days = clist(config, 'Schedule', option, rtype='int')
      elif option == 'times of the day':
        self.time_of_day = clist(config, 'Schedule', option)
  
  def update_schedule(self, config):
    config.add_section('Schedule')
    config.set('Schedule', 'Days of the Week', ','.join(["%s" % el for el in self.days_of_week]))
    config.set('Schedule', 'Weeks of the Month', ','.join(["%s" % el for el in self.weeks_of_month]))
    config.set('Schedule', 'Calendar Days', ','.join(["%s" % el for el in self.calendar_days]))
    config.set('Schedule', 'Times of the Day', ','.join(["%s" % el for el in self.time_of_day]))
    config.set('Schedule', 'Recurring', self.recurring)
    return config
  
  def _get_current_time(self):
    year, month, date, hour, minute, sec, dow = time.localtime(time.time())[:7]
    calendar.setfirstweekday(calendar.SUNDAY)
    cal = calendar.month(year, month).split('\n')[2:]
    wom = 0
    for week in cal:
      for day in week.split():
        if int(day) == int(date):
          wom = cal.index(week) + 1
    return {           'date': date, 
                'day_of_week': dow, 
                       'time': '%02d:%02d' % (hour, minute),
                     'minute': minute,
                       'hour': hour,
                      'ftime': '%02d:%02d' % (hour, minute/5*5),
              'week_of_month': wom
             }

  def export(self):
    return {  'days_of_week': self.days_of_week,
            'weeks_of_month': self.weeks_of_month,
               'time_of_day': self.time_of_day,
             'calendar_days': self.calendar_days,
                 'recurring': self.recurring,
            }
  
  def _import(self, idict):
    self.days_of_week   = idict['days_of_week']
    self.weeks_of_month = idict['weeks_of_month']
    self.time_of_day    = idict['time_of_day']
    self.calendar_days  = idict['calendar_days']
    self.recurring      = idict['recurring']

class NmapScan(object):
  nmap          = None
  name          = None
  options       = []
  ip_addresses  = []
  schedule      = Scheduler()
  scan_id       = None
  conf          = Configuration()
  _ex_scan      = False
  _ex_status    = None
  runtime       = None
  scanner       = None
  
  def __init__(self, name=None, 
                     scantype='file',
                     scan_id=None, 
                     options=[],
                     ip_addresses=[],
                     idict={}):
    if scantype == 'file':
      if scan_id is not None:
        self.parse_scanfile(scan_id)
      else:
        raise Exception('No Scan ID Specified')
    elif scantype == 'import':
      self._import(idict)
    elif scantype == 'new':
      idc = hashlib.md5()
      idc.update(name)
      idc.update(time.strftime('%Y%m%D-%H%M%S'))
      self.name         = name
      self.ip_addresses = ip_addresses
      self.options      = options
      self.scan_id      = idc.hexdigest()
      self.set_nmap_command()
  
  def set_nmap_command(self):
    if self.conf.is_scanner:
      if self.status() == 'waiting':
        out = '-oX %s/%s.xml' % (self.conf.xmlout, self.scan_id)
        if out not in self.options:
          self.options.append(out)
        cmd = 'nmap %s %s' % (' '.join(self.options), 
                              ' '.join(self.ip_addresses))
        self.nmap = NmapCommand.NmapCommand(cmd)
      else:
        raise Exception('Cannot change nmap command when scan has started or completed')
  
  def status(self):
    if not self._ex_scan:
      try:
        status = self.nmap.scan_state()
      except Exception:
        return 'waiting'
      else:
        if status:
          return 'running'
        else:
          return 'completed'
    else:
      return self._ex_status
  
  def run_scan(self, now=False):
    if self.conf.is_scanner:
      if not now:
        if self.schedule.check():
          self.nmap.run_scan()
          self.runtime = time.time()
      else:
        self.nmap.run_scan()
        self.runtime = time.time()
      self.update_scanfile()
  
  def eta(self):
    pass
  
  def hosts_completed(self):
    pass
  
  def total_host(self):
    pass
  
  def cleanup(self):
    pass
  
  def update_scanfile(self):
    config = ConfigParser.ConfigParser()
    config.add_section('Scan')
    config.set('Scan', 'Name', self.name)
    config.set('Scan', 'Scan ID', self.scan_id)
    config.set('Scan', 'Options', ','.join(self.options))
    config.set('Scan', 'IP Addresses', ','.join(self.ip_addresses))
    config.set('Scan', 'Status', self.status())
    config.set('Scan', 'Runtime', self.runtime)
    config.set('Scan', 'Scanner', self.scanner)
    self.schedule.update_schedule(config)
    with open('%s/%s.scan' % (self.conf.scanfiles, self.scan_id), 'w') as cfile:
      config.write(cfile)
  
  def parse_scanfile(self, scan_id):
    config = ConfigParser.ConfigParser()
    config.read('%s/%s.scan' % (self.conf.scanfiles, scan_id))
    for option in config.options('Scan'):
      if option == 'name':
        self.name = config.get('Scan', 'Name')
      elif option == 'scan id':
        self.scan_id = config.get('Scan', 'Scan ID')
      elif option == 'options':
        self.options = clist(config, 'Scan', option)
      elif option == 'ip addresses':
        self.ip_addresses = clist(config, 'Scan', option)
      elif option == 'scanner':
        self.scanner = config.get('Scan', 'Scanner')
      elif option == 'status':
        if config.get('Scan', 'Status') != 'waiting':
          self._ex_scan = True
          self._ex_status = config.get('Scan', 'Status')
      elif option == 'runtime':
        self.runtime = config.get('Scan', 'Runtime')
        if self.runtime == 'None':
          self.runtime = None
    self.schedule.parse_schedule(config)
    if not self._ex_scan:
      self.set_nmap_command()
  
  def check(self):
    addresses = get_ip_addresses()
    if conf.zones[self.scanner] in addresses:
      return self.schedule.check()
    else:
      return False
  
  def get_results(self):
    results = []
    for line in open('%s/%s.xml' % (self.conf.xmlout, self.scan_id), 'r'):
      results.append(line)
    return '\n'.join(results)
  
  def export(self):
    return {'scan': {        'name': self.name,
                          'options': self.options,
                     'ip_addresses': self.ip_addresses,
                          'scan_id': self.scan_id,
                          'scanner': self.scanner,
                          'runtime': self.runtime
                     },
        'schedule': self.schedule.export()}
  
  def _import(self, idict):
    self.name         = idict['scan']['name']
    self.options      = idict['scan']['options']
    self.ip_addresses = idict['scan']['ip_addresses']
    self.scan_id      = idict['scan']['scan_id']
    self.scanner      = idict['scan']['scanner']
    self.runtime      = idict['scan']['runtime']
    self.schedule._import(idict['schedule'])
    

def clist(config, stanza, option, rtype='string', delim=','):
  ret = []
  objlist = config.get(stanza, option).split(delim)
  for obj in objlist:
    if rtype == 'int':
      if obj is not '':
        ret.append(int(obj))
    elif rtype == 'string':
      ret.append(obj)
  return ret

def get_scans():
  scans = []
  conf = Configuration()
  for scanfile in os.listdir(conf.scanfiles):
    scan_id = scanfile.split('.')[0]
    scans.append(NmapScan(scan_id=scan_id))
  return scans

def get_ip_address():
  addresses = []
  for line in commands.getoutput('/sbin/ifconfig -a').split('\n'):
    if line.find('\tinet ') > -1:
      addresses.append(line.split()[1])
  return addresses