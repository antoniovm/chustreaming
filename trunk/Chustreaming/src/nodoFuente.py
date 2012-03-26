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
        self.cabecera = ""
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
        print "Conexion establecida con Icecast."
        
    def getPaquete(self, i):
        return self.cabecera[1024*i:1024*(i+1)];
        
    def aceptarConexionTCP(self, tamCab):
        i=0
        print "Esperando aceptar conexion TCP por parte del peer"
        (self.socketClienteTCP, self.direccionCliente) = self.socketServerTCP.accept()
        print "Conexion aceptada"
        print "Direccion cliente: ", self.direccionCliente
        print "Enviando cabecera..."
        while i < tamCab:
            self.socketClienteTCP.send(self.getPaquete(i))
            print "Paquete ", i, " enviado."
            i += 1
        print "Cabecera enviada."        
        self.enviarClienteUDP()
        
    def enviarClienteUDP(self):
        self.socketClienteUDP = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        #self.socketClienteUDP.sendto(msg, self.direccionCliente)
        
        
    def eliminarCabeceraHTTP(self, chunk):
        #Eliminar la cabecera HTTP
        #posicionNumeroMagico = chunk.find("OggS") #Posicion en la que se encuentra OggS 
        #if posicionNumeroMagico < 0:
        #    chunk = ''
        #    return chunk
        #else:
        #    chunk = chunk[posicionNumeroMagico:]    #Forma de indexar subcadenas
            return chunk          
                        
    def recibirCabecera(self):
        #f = open("C:\\Users\\" + "Loop" + "\\Desktop\\" + "serverBunny" + ".ogg", "w")
        i = 0
        numeroBloque = 0
        while i < 10:
            msg = ''
            while len(msg) < self.MSGLEN:
                chunk = self.socketIcecast.recv(self.MSGLEN-len(msg))
                
                if chunk == '':
                    raise RuntimeError("socket connection broken icecast")
                msg = msg + chunk
                
            #numeroBloque=(numeroBloque+1)%(2**16)
            #binario = pack(">H", numeroBloque) #Codificado como short big-endian
            #msg = binario + msg
            #self.socketClienteUDP.sendto( msg, (self.direccionCliente[0], 12000))
            #self.socketClienteTCP.send(msg)
            #f.write(msg);
            self.cabecera += msg
            i += 1
            print "Recibido bloque ", i
        #f.close()
        

        
    def hiloLeerIcecast(self):
        numeroBloque = 0;
        #f = open("C:\\Users\\" + "Loop" + "\\Desktop\\" + "serverBunny" + ".ogg", "a")
        while True:
            msg = ''
            while len(msg) < self.MSGLEN:
                chunk = self.socketIcecast.recv(self.MSGLEN-len(msg))
                
                if chunk == '':
                    print RuntimeError("socket connection broken icecast")
                    continue
                
                msg = msg + chunk
                
                
                              
                
                
            numeroBloque=(numeroBloque+1)%(2**16)
            binario = pack(">H", numeroBloque) #Codificado como short big-endian
            msg = binario + msg
            #f.write(msg[2:]);
            if (self.socketClienteUDP is not None):
                self.socketClienteUDP.sendto(msg, self.direccionCliente)
                print numeroBloque, " bloque enviado"; #Para mostrar cuantos bloques de bytes vamos leyendo
            

nodoFuente = NodoFuente()
nodoFuente.conectarIcecast()
nodoFuente.recibirCabecera()
thread.start_new_thread(nodoFuente.aceptarConexionTCP,(10,))
nodoFuente.hiloLeerIcecast()

        