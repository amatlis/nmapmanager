from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from zenmapCore         import NmapParser
from zenmapCore         import NmapCommand

class RPCService(object):
  queue   = []
  sensor  = None
  config  = config.Config()
  def __init__(self, sensor):
    self.sensor = sensor
  
  def queue_add(self, name, sensor, time, networks):
    if sensor == self.sensor:
      queue.append({    'name': name,
                        'time': time,
                    'networks': networks,
                      'status': 'waiting'})
      return '%s added to queue' % name
    else:
      return 'ERROR: %s is not %s' % (sensor, self.sensor)
  
  def queue_del(self, scan_id):
    pass
  
  def _add_scan(self, name, time, networks):
    