'''
Created on 06/03/2012

@author: jorge, antonio
'''
#import httplib
#conn = httplib.HTTPConnection("localhost:8000")
#conn.request("GET", "/lista.ogg")
#r1 = conn.getresponse()
#print r1.status, r1.reason
#data1 = r1.read()
#f = open('/mnt/hgfs/Chustafile/Tercer curso/Segundo cuatrimestre/Redes/Streaming/recepcion/tangerineDream.ogg', 'w')
#print >> f, data1
#print data1
#conn.close()

import socket
MSGLEN = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 8000))
s.send("GET /prueba.ogg HTTP/1.1\r\n\r\n")
ruta = raw_input("Introduce la ruta de destino de la captura");
f = open(ruta, "w")
#f = open("/home/jorge/Escritorio/bunny.ogg", "w")
while 1:
    msg = ''
    while len(msg) < MSGLEN:
        chunk = s.recv(MSGLEN-len(msg))
        if chunk == '':
            raise RuntimeError("socket connection broken")
        msg = msg + chunk
    print >> f, msg
    print msg;