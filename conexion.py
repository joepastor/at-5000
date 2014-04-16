#!/usr/bin/env python
import MySQLdb, sys
try:
	db = MySQLdb.connect(host='172.16.40.4',user='siap',passwd='tr0nch4',db='siap')
	session = db.cursor()
except MySQLdb.Error, e:
	print e
	sys.exit(0)

