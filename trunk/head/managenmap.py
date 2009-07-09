#!/bin/env python

import os
import sys
import commands
import readline
import cmd
import nmap

class CLI(cmd.Cmd):
  def __init__(self):
    cmd.Cmd.__init__(self)
    self.prompt = "nmap manager>"
  
  def help_help(self):
    print '\n'.join(['syntax: help [topic]',
                     '        Display help information.'
                    ])
  
  def do_config(self, arg):
    pass
    # update, new, del
  
  def do_scan(self, arg):
    pass
    # with, all, ad-hoc
  
  def do_report(self, arg):
    pass
    # network, range
    #
    # Default comparing the most recent scan with the scan before it.
    # however allow for the user to override this functionality and get
    # a larger range of data.
  

def main():
  cli = CLI()
  cli.cmdloop()

if __name__ == '__main':
  main()