'''
Created on 06/03/2012

@author: jorge, antonio, miguel
'''

import socket
from struct import pack
MSGLEN = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "Introduzca la IP del peer"
#ruta = raw_input();
ruta = "172.20.37.162"
s.connect((ruta, 12000))
print "Conexion realizada"

print "Peticion enviada"

while True:
    print ">"
    msg = raw_input()
    s.send(msg)
    print s.recv(1024)
    
