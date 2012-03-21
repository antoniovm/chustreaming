'''
Created on 06/03/2012

@author: jorge, antonio, miguel
'''

import socket
from struct import pack

class nodoFuente:
    def __init__(self):
        self.MSGLEN = 1024
        
        self.socketIcecast = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.socketServerTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket TCP cabecera Ogg
        self.socketClienteTCP = None
        self.socketClienteUDP = None
        self.direccionCliente = '' #(ip, puerto) de haber hecho accept
        
        self.socketTCP.bind(('', 12000))
        self.socketTCP.listen(1)
        
    def conectarIcecast(self):
        self.socketIcecast.connect(('localhost', 8000))
        self.socketIcecast.send("GET /canal1 HTTP/1.1\r\n\r\n")
        
    def aceptarConexionTCP(self):
        (self.socketClienteTCP, self.direccionCliente) = self.socketServerTCP.accept()
        
    def enviarClienteUDP(self):
        self.socketClienteUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socketClienteUDP.sendto(msg, self.direccionCliente)
        
    def eliminarCabeceraHTTP(self):
        respuestaServidor = 0;
        posicionNumeroMagico = -1 #Donde se guardara la posicion en la que se encuentra OggS
    
        while True:
                chunk = self.socketIcecast.recv(self.MSGLEN)
                
                if chunk == '':
                    raise RuntimeError("socket connection broken")
                    
                
                #Eliminar la cabecera HTTP
                if respuestaServidor == 0: #Para buscar el numero magico solo una vez
                    posicionNumeroMagico = chunk.find("OggS")
                    if posicionNumeroMagico < 0:
                        continue
                    else:
                        chunk = chunk[posicionNumeroMagico:]    #Forma de indexar subcadenas
                        return chunk          
                        
                           
    def hiloLeerIcecast(self):
        numeroBloque = 0;
        while 1:
            msg = self.eliminarCabeceraHTTP()
            while len(msg) < self.MSGLEN:
                chunk = self.socketIcecast.recv(self.MSGLEN-len(msg))
                
                if chunk == '':
                    raise RuntimeError("socket connection broken")
                              
                        
                msg = msg + chunk
                
            numeroBloque=(numeroBloque+1)%(2**16)
            binario = pack(">H", numeroBloque) #Codificado como short big-endian
            msg = binario + msg
            self.socketClienteUDP.sendto( msg, self.direccionCliente)
            print numeroBloque, " bloque enviado"; #Para mostrar cuantos bloques de bytes vamos leyendo
            
    #hiloLeerIcecast();
        