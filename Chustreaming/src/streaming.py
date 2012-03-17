'''
Created on 06/03/2012

@author: jorge, antonio, miguel
'''

import socket
from struct import pack
MSGLEN = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "Introduzca la IP del servidor"
ruta = raw_input();
s.connect((ruta, 8000))
s.send("GET /prueba HTTP/1.1\r\n\r\n")
respuestaServidor = 0;
posicionNumeroMagico = -1 #Donde se guardara la posicion en la que se encuentra OggS
i = 0;

UDP_IP="127.0.0.1"
UDP_PORT=5005

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT

sock = socket.socket( socket.AF_INET, # Internet
                      socket.SOCK_DGRAM ) # UDP

while 1:
    msg = ''
    while len(msg) < MSGLEN:
        chunk = s.recv(MSGLEN-len(msg))
        
        if chunk == '':
            raise RuntimeError("socket connection broken")
            
        
        #Eliminar la cabecera HTTP
        if respuestaServidor == 0: #Para buscar el numero magico solo una vez
            posicionNumeroMagico = chunk.find("OggS")
            if posicionNumeroMagico < 0:
                continue
            else:
                respuestaServidor = 1
                chunk = chunk[posicionNumeroMagico:]    #Forma de indexar subcadenas          
                
        msg = msg + chunk
        
    i=(i+1)%(2**16)
    binario = pack(">H", i) #Codificado como short big-endian
    msg = binario + msg
    sock.sendto( msg,(UDP_IP, UDP_PORT))
    print i, " bloque enviado"; #Para mostrar cuantos bloques de bytes vamos leyendo