'''
Created on 06/03/2012

@author: jorge, antonio, miguel
'''

import socket
MSGLEN = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(("localhost", 8000))
s.send("GET /prueba.ogg HTTP/1.1\r\n\r\n")
ruta = raw_input("Introduce la ruta de destino de la captura: ");
f = open(ruta, "w")
respuestaServidor = 0; 
posicionNumeroMagico = -1
i = 0;
while 1:
    msg = ''
    while len(msg) < MSGLEN:
        chunk = s.recv(MSGLEN-len(msg))
        
        if chunk == '':
            raise RuntimeError("socket connection broken")
            continue
        
        
        if respuestaServidor == 0: #Para buscar el numero magico solo una vez
            posicionNumeroMagico = chunk.find("OggS")
            if posicionNumeroMagico < 0:
                continue
            else:
                respuestaServidor = 1
                chunk = chunk[posicionNumeroMagico:]    #Forma de indexar subcadenas          
                
        msg = msg + chunk
    print >> f, msg
    i=i+1
    print i, " bloque obtenido";
    if i >= 2000:
        f.close()
        break