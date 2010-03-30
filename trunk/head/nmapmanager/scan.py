import xmlrpclib

class NmapScan(object):
  time      = None
  networks  = []
  sensor    = None
  
  def __init__(self, time, sensor, networks):
    self.time     = time
    self.sensor   = sensor
    self.networks = networks
  
  def run_scan(self):
    sensor = sensors.get_sensor(self.sensor)
    sensor.add_to_queue(self)


class Sensor(object):
  url        = None
  proxy      = None
  def __init__(self, url):
    self.url      = url
    self.proxy    = xmlrpclib.ServerProxy(self.url)
  
  def queue_add(self, scan):
    return self.proxy.queue_add(scan.sensor, scan.time, scan.networks)
  
  def queue_list(self):
    return self.proxy.queue_list()
  
  def queue_del(self, scan_id):
    return self.proxy.queue_del(scan_id)
  
  def is_scanning(self):
    return self.proxy.is_scanning()
  
  def get_scan(self, scan_id):
    return self.proxy.get_scan_results(scan_id)
    
    