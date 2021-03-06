#!/usr/bin/python                                                                                                        

import os
from os.path import join, getsize
import sys
import psycopg2
import psycopg2.extensions
import psycopg2.extras
from optparse import OptionParser
from distutils import version
import datetime
import re
import subprocess

parser = OptionParser()
parser.add_option("-P", "--path", dest="path",
                  help="path to the upgrade directory",
                  metavar="DIRPATH", default="/data/socorro/application/sql/upgrade")
parser.add_option("-D", "--database", dest="dbname",
                  help="database to upgrade", metavar="DBNAME",
                  default="breakpad")
parser.add_option("-p", "--port", dest="dbport",
                  help="database port", metavar="DBPORT",
                  default="5432")
parser.add_option("-H", "--host", dest="dbhost",
                  help="database hostname", metavar="DBHOST",
                  default="localhost")
parser.add_option("-l", "--log", dest="logfile",
                  help="logfile location for output",
                  metavar="LOGFILE", default="socorro_upgrade.log")
(options, args) = parser.parse_args()

# get list of upgrade directories                                                                                        

alldirs = []
for root, dirs, files in os.walk(options.path):
    alldirs = dirs
    break

# filter list for only numerical upgrades                                                                                

updirs = [dir for dir in alldirs if re.match('\d+\.\d+',dir)]

# sort                                                                                                                   

updirs.sort(key=version.LooseVersion)

#get current DB version                                                                                                 
conn = psycopg2.connect("dbname=%s user=postgres host=%s port=%s"
                        % ( options.dbname, options.dbhost, options.dbport, ) )                                         
cur = conn.cursor()                                                                                                     
cur.execute(""" SELECT version                                                                                          
            FROM socorro_db_version""")                                                                                 
cur_version = version.LooseVersion(str(cur.fetchone()[0]))                                                              
conn.disconnect                                                                                                         

#logfile                                                                                                                 
logfile = open(options.logfile, 'a')
logfile.write('\n\n********************************************************\n')
logfile.write("began upgrade at %s \n\n" % str(datetime.datetime.now()))
logfile.flush()

# compare each directory in the list to the DB version                                                                   
for updir in updirs:
    # if greater than installed, execute                                                                                 
    curdir = version.LooseVersion(updir)
    if cur_version < curdir:
        # upgrade commands need to be executed from the shell as "postgres"                                              
        upcmd = os.path.join(options.path, updir, 'upgrade.sh')
        upresult = subprocess.call(upcmd, stdout=logfile, stderr=logfile, shell=True)
        if upresult <> 0:
            # if we failed, print output, raise error and note it in the log                                             
            print "upgrade for version %s failed with error code %n." % ( updir, upresult, )
            print "check the error log at %s", options.logfile
            logfile.write("\n upgrade failed on version %s at %s" % (updir, str(datetime.datetime.now()),))
            logfile.close
            sys.exit(1)
    finaldir = updir

#looks like we succeeded.  finish log, close and exit.                                                                   
print "upgrades complete, upgraded to %s" % finaldir
logfile.write("completed upgrade to version %s at %s \n\n" % (finaldir, str(datetime.datetime.now()),))
logfile.close
sys.exit(0)