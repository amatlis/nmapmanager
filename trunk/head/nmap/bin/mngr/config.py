import ConfigParser

class Configuration(object):
  scanfiles     = '/opt/nmap/scans'
  xmlout        = '/opt/nmap/xml'
  bin           = '/opt/nmap/bin'
  config        = '/opt/nmap/nmap.conf'
  tmp           = '/opt/nmap/tmp'
  scanner       = '%s/scanner.py'
  is_scanner    = True
  zones         = {'all': '127.0.0.1'}
  address       = '127.0.0.1'
  port          = 12288
  def __init__(self):
    pass