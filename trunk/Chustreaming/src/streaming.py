'''
Created on 06/03/2012

@author: jorge
'''
import httplib
conn = httplib.HTTPConnection("localhost:8000")
conn.request("GET", "/emitiendo.ogg")
r1 = conn.getresponse()
print r1.status, r1.reason
data1 = r1.read()
f = open('/home/jorge/Documentos/canciones/streamPython.ogg', 'w')
print >> f, data1
print data1
conn.close()

#data = "holaaa me llamo pericoooo"
#f = open('/home/jorge/Documentos/canciones/streamPython.txt', 'w')
#print >> f, data