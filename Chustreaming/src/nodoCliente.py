'''
Created on 15/03/2012

@author: jorge
'''
import socket
import getpass
MSGLEN = 1024
i=0;
UDP_IP="127.0.0.1"
UDP_PORT=5005 
sock = socket.socket( socket.AF_INET, # Internet
                      socket.SOCK_DGRAM ) # UDP
sock.bind( (UDP_IP,UDP_PORT) )

#ruta = raw_input("Introduce la ruta de destino de la captura: "); #Incluyendo nombre del archivo .ogg destino
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
        f.write(msg);
    i=i+1
    print i, " bloque obtenido"; #Para mostrar cuantos bloques de bytes vamos leyendo