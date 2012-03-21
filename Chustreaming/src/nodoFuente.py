'''
Created on 06/03/2012

@author: jorge, antonio, miguel
'''

import socket
from struct import pack
MSGLEN = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print "Introduzca la IP del peer"
ruta = raw_input();
ruta = "localhost"
s.connect((ruta, 8000))
s.send("GET /canal1 HTTP/1.1\r\n\r\n")
respuestaServidor = 0;
posicionNumeroMagico = -1 #Donde se guardara la posicion en la que se encuentra OggS
numeroBloque = 0;

UDP_IP="localhost"
UDP_PORT=8080

print "UDP target IP:", UDP_IP
print "UDP target port:", UDP_PORT

sock = socket.socket( socket.AF_INET, # Internet
                      socket.SOCK_DGRAM ) # UDP


    
def hiloLeerIcecast():
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
            
        numeroBloque=(numeroBloque+1)%(2**16)
        binario = pack(">H", numeroBloque) #Codificado como short big-endian
        msg = binario + msg
        sock.sendto( msg,(UDP_IP, UDP_PORT))
        print numeroBloque, " bloque enviado"; #Para mostrar cuantos bloques de bytes vamos leyendo
        
hiloLeerIcecast();
    