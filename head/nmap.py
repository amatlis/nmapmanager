import ConfigParser, datetime, os

CONFIG = "nmap.ini"

class Scanner(object):
  def __init__(self, zone, name, user, address, options, tasks):
    self.name     = name
    self.zone     = zone
    self.user     = user
    self.tasks    = tasks
    self.address  = address
    self.options  = options

class Task(object):
  def __init__(self, zone, name, time, ip_range, options):
    self.name     = name
    self.zone     = zone
    self.time     = time
    self.ip_range = ip_range
    self.options  = options

class Host(object):
  def __init__(self, gnmap_entry):
    self.ip = 'none'
    self.hostname = 'none'
    self.ports = []
    self.os = []
    self.parse_gnmap(gnmap_entry)

  def parse_gnmap(self, entry):
    self.ip = entry.split('\t')[0].split(':')[1].split()[0]
    self.hostname = entry.split('\t')[0].split(':')[1].split()[1].strip('()')
    port_list = entry.split('\t')[1].split(',')    

    for item in port_list:
      if item.find('Ports') != -1:
        number = item.split('/')[0].split(':')[1].strip()
      else:
        number = item.split('/')[0].strip()
      status = item.split('/')[1].strip()
      proto = item.split('/')[2].strip()
      info = item.split('/')[4]
      banner = item.split('/')[6]
      self.ports.append(Port(number, status, proto, info, banner))


class Port(object):
  def __init__(self, number, status, proto, info, banner):
    self.number = number
    self.status = status
    self.protocol = proto
    self.info = info
    self.banner = banner

def load_config(file):
  config = ConfigParser.RawConfigParser()
  config.read(file)
  
  configuration = {
               'nmap': config.get('Global Options', 'Nmap Options'),
            'ssh key': config.get('Global Options', 'SSH Key'),
      'data location': config.get('Global Options', 'Data Location'),
              'debug': config.get('Global Options', 'Debug')
  }
  
  active_scanners = config.get('Global Options', 'Active Scanners').split(',')
  
  scanners = []
  
  for active_scanner in active_scanners:
    s_name    = config.get('%s scanner' % active_scanner, 'Name')
    s_user    = config.get('%s scanner' % active_scanner, 'SSH User')
    s_address = config.get('%s scanner' % active_scanner, 'IP Address')
    s_nmap    = config.get('%s scanner' % active_scanner, 'Nmap Options')
    s_tasks   = config.get('%s scanner' % active_scanner, 'Active Tasks').split(',')

    tasks     = []
    
    for s_task in s_tasks:
      name = config.get('%s task' % s_task, 'Name')
      time = config.get('%s task' % s_task, 'Scan Time')
      nmap = config.get('%s task' % s_task, 'Nmap Options')
      ips  = config.get('%s task' % s_task, 'IP Range')
      
      tasks.append(Task(s_task,name,time,ips,nmap))
    
    scanners.append(Scanner(active_scanner,s_name,s_user,s_address,s_nmap,tasks))
  return configuration,scanners

def run_scan(config, scanner, task):
  
  if task.options != "":
    opts = task.options
  elif scanner.options != "":
    opts = scanner.options
  else:
    opts = config['nmap']
  
  # This section is a complete mess.  I'll have to tidy it up once I have a 
  # more efficient way to do this that is actually somewhat readable.
  date          = datetime.date.today().strftime('%Y-%m-%d')
  ssh_agent     = '$(ssh-agent);ssh-add %s' % config['ssh key']
  nmap_command  = 'nmap %s -oA /tmp/nmap-%s-%s %s' % (opts, task.name.strip(), date, task.ip_range)
  ssh_statement = 'ssh %s@%s "%s"' % (scanner.user, scanner.address, nmap_command)
  command       = '%s;%s' % (ssh_agent,ssh_statement)
  nmap_command      = command
  retrieve_command  = 'scp %s@%s:/tmp/nmap-%s-%s* %s' % (scanner.user, scanner.address, task.name.strip(), date, config['data location'])
  
  if config['debug']:
    print "    Nmap Command : %s" % nmap_command
    print "Retreive Command : %s" % retrieve_command
  
  os.system(nmap_command)
  os.system(retrieve_command)

def generate_report(config, task):
  # This has yet to be done.
  print "This is incomplete"
  
  today         = datetime.date.today().strftime('%Y-%m-%d')
  yesterday     = datetime.date.yesterday().strftime('%Y-%m-%d')
  
  