'''
Created on 15/03/2012

@author: jorge, antonio, miguel
'''
import socket
import getpass          
import os               #Para obtener datos del sistema operativo
from struct import unpack #Para desempaquetar cadenas de bytes
MSGLEN = 1026
numeroBloque=0;
i=0;  
UDP_IP="87.216.135.207"
UDP_PORT=8080 
sock = socket.socket( socket.AF_INET, # Internet
                      socket.SOCK_DGRAM ) # UDP

sock.bind( (UDP_IP,UDP_PORT) )

#ruta = raw_input("Introduce la ruta de destino de la captura: "); #Incluyendo nombre del archivo .ogg destino
if(os.name == 'nt'): #Windows
    ruta = "C:\\Users\\" + getpass.getuser() + "\\Desktop\\bunny.ogg"
else:
    ruta = "/home/" + getpass.getuser() + "/Escritorio/bunny.ogg"
f = open(ruta, "w")

print "PEER STARTED"
while True:
    msg = ''
    while len(msg) < MSGLEN:
        chunk = sock.recv(MSGLEN-len(msg)) 
        if chunk == '':
            print RuntimeError("socket connection broken")
            continue
        
        msg = msg + chunk
        #print "received message:", msg
    
    numeroBloque=unpack(">H", msg[:2])[0] #Seleccionamos los 2 primeros bytes
    f.write(msg[2:]); #Escribimos el resto en el fichero
    i = i +1
    print i, " Iteracion - ", numeroBloque, " bloque obtenido"; 