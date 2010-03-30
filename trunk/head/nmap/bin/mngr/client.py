import xmlrpclib
from config import Configuration

class Zone(object):
  conf = Configuration()
  def __init__(self, name):
    self.ip     = self.conf.zones[name]
    self.port   = self.conf.port
    self.proxy  = xmlrpclib.ServerProxy('http://%s:%s' % (self.ip, self.port),
                                        allow_none=True)
    self.name   = name
  
  def has_completed(self):
    queue = self.list_queue()
    for scan in queue:
      if queue[scan]['status'] == 'completed':
        return True
    return False
  
  def get_completed(self):
    completed_scans = []
    queue           = self.list_queue()
    for scan in queue:
      if queue[scan]['status'] == 'completed':
        completed_scans.append(scan)
    return completed_scans
  
  def get_results(self, scan_id):
    return str(self.proxy.scanresults(scan_id))
  
  def remove_from_queue(self, scan_id):
    return self.proxy.queuedel(scan_id)
  
  def add_to_queue(self, scan):
    return self.proxy.queueadd(scan)
  
  def list_queue(self):
    return self.proxy.queuelist()
  
  def get_details(self, scan_id):
    return self.proxy.scan(scan_id)