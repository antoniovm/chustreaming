'''
Created on 15/03/2012

@author: jorge
'''
import socket
import getpass
import sys
import os
from struct import unpack
MSGLEN = 1026
i=0; 
UDP_IP="localhost"
UDP_PORT=12000 
sock = socket.socket( socket.AF_INET, # Internet
                      socket.SOCK_DGRAM ) # UDP

sock.bind( (UDP_IP,UDP_PORT) )

#ruta = raw_input("Introduce la ruta de destino de la captura: "); #Incluyendo nombre del archivo .ogg destino
if(os.name == 'nt'):
    ruta = "C:\\Users\\" + getpass.getuser() + "\\Desktop\\bunny.ogg"
else:
    ruta = "/home/" + getpass.getuser() + "/Escritorio/bunny.ogg"
f = open(ruta, "w")

print "PEER STARTED"
while True:
    msg = ''
    while len(msg) < MSGLEN:
        chunk, addr = sock.recvfrom(MSGLEN-len(msg)) # buffer size is 1024 bytes
        if chunk == '':
            print RuntimeError("socket connection broken")
            continue
        
        msg = msg + chunk;
        #print "received message:", msg
    
    i=unpack(">H", msg[:2])[0]
    f.write(msg[2:]);
    print i, " bloque obtenido"; #Para mostrar cuantos bloques de bytes vamos leyendo