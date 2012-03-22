'''
Created on 06/03/2012

@author: jorge, antonio, miguel
'''

import socket
import thread
from struct import pack

class NodoFuente:
    def __init__(self):
        self.MSGLEN = 1024
        
        self.socketIcecast = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        self.socketServerTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket TCP cabecera Ogg
        self.socketClienteTCP = None
        self.socketClienteUDP = None
        self.direccionCliente = '' #(ip, puerto) de haber hecho accept
        
        self.socketServerTCP.bind(('', 12000))
        self.socketServerTCP.listen(1)
        
    def conectarIcecast(self):
        self.socketIcecast.connect(('localhost', 8000))
        self.socketIcecast.send("GET /canal1 HTTP/1.1\r\n\r\n")
        
    def aceptarConexionTCP(self):
        print "Esperando aceptar conexion TCP por parte del peer"
        (self.socketClienteTCP, self.direccionCliente) = self.socketServerTCP.accept()
        print "Conexion aceptada"
        print "Direccion cliente: ", self.direccionCliente
        
    def enviarClienteUDP(self):
        self.socketClienteUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.socketClienteUDP.sendto(msg, self.direccionCliente)
        thread.start_new_thread(self.hiloLeerIcecast())
        
    def eliminarCabeceraHTTP(self, chunk):
        #Eliminar la cabecera HTTP
        posicionNumeroMagico = chunk.find("OggS") #Posicion en la que se encuentra OggS 
        if posicionNumeroMagico < 0:
            chunk = ''
            return chunk
        else:
            chunk = chunk[posicionNumeroMagico:]    #Forma de indexar subcadenas
            return chunk          
                        
    def enviarCabeceraOgg(self):
        i = 0
        numeroBloque = 0
        respuestaServidor = 0
        while i < 10:
            msg = ''
            while len(msg) < self.MSGLEN:
                chunk = self.socketIcecast.recv(self.MSGLEN-len(msg))
                
                if chunk == '':
                    print RuntimeError("socket connection broken icecast")
                    continue
                
                if respuestaServidor == 0: #Para buscar el numero magico solo una vez
                    chunk = self.eliminarCabeceraHTTP(chunk)
                    if chunk == '':
                        continue
                    else:
                        respuestaServidor = 1
                              
                msg = msg + chunk
                
            #numeroBloque=(numeroBloque+1)%(2**16)
            #binario = pack(">H", numeroBloque) #Codificado como short big-endian
            #msg = binario + msg
            #self.socketClienteUDP.sendto( msg, (self.direccionCliente[0], 12000))
            self.socketClienteTCP.send(msg)
            print numeroBloque, " bloque enviado"; #Para mostrar cuantos bloques de bytes vamos leyendo
            i += 1
            print "Vuelta NodoFuente ", i
        
                               
    def hiloLeerIcecast(self):
        respuestaServidor = 1;
        numeroBloque = 0;
        while True:
            msg = ''
            while len(msg) < self.MSGLEN:
                chunk = self.socketIcecast.recv(self.MSGLEN-len(msg))
                
                if chunk == '':
                    print RuntimeError("socket connection broken icecast")
                    continue
                
                if respuestaServidor == 0: #Para buscar el numero magico solo una vez
                    chunk = self.eliminarCabeceraHTTP(chunk)
                    if chunk == '':
                        continue
                    else:
                        respuestaServidor = 1
                              
                msg = msg + chunk
                
            numeroBloque=(numeroBloque+1)%(2**16)
            binario = pack(">H", numeroBloque) #Codificado como short big-endian
            msg = binario + msg
            self.socketClienteUDP.sendto( msg, (self.direccionCliente[0], 12000))
            print numeroBloque, " bloque enviado"; #Para mostrar cuantos bloques de bytes vamos leyendo
            

nodoFuente = NodoFuente()
nodoFuente.aceptarConexionTCP()
nodoFuente.conectarIcecast()
nodoFuente.enviarCabeceraOgg()
nodoFuente.enviarClienteUDP()
        