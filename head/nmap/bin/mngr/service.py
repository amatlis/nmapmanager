from SimpleXMLRPCServer import SimpleXMLRPCServer
from SimpleXMLRPCServer import SimpleXMLRPCRequestHandler
from config import Configuration
from daemon import daemonize
import os
import scanning

class RequestHandler(SimpleXMLRPCRequestHandler):
    rpc_paths = ('/RPC2',)

class XMLRPCService(object):
  conf = Configuration()
  
  def queuedel(self, scan_id):
    scan = scanning.NmapScan(scan_id=scan_id)
    if scan.status() == 'completed':
      try:
        os.remove('%s/%s.scan' % (self.conf.scanfiles,  scan_id))
      except OSError:
        pass
      try:
        os.remove('%s/%s.log'  % (self.conf.tmp,        scan_id))
      except OSError:
        pass
      try:
        os.remove('%s/%s.xml'  % (self.conf.xmlout,     scan_id))
      except OSError:
        pass
      return True
    else:
      return False
  
  def queueadd(self, scan_dict):
    scan = scanning.NmapScan(scantype='import', idict=scan_dict)
    scan.update_scanfile()
    return True
  
  def queuelist(self):
    ret = {}
    scans = scanning.get_scans()
    for scan in scans:
      ret[scan.scan_id] = {'status': scan.status()}
    return ret
  
  def scan(self, scan_id):
    scan = scanning.NmapScan(scan_id=scan_id)
    return scan.export()
  
  def scanresults(self, scan_id):
    scan = scanning.NmapScan(scan_id=scan_id)
    return scan.get_results()

def run_server():
  #daemonize()
  conf = Configuration()
  server = SimpleXMLRPCServer((conf.address, conf.port), 
                              requestHandler=RequestHandler, allow_none=True)
  server.register_instance(XMLRPCService())
  server.serve_forever()
  