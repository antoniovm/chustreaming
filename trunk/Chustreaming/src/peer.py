'''
Created on 15/03/2012

@author: jorge, antonio, miguel
'''
import socket
import getpass
import sys          
import os               #Para obtener datos del sistema operativo
from struct import unpack #Para desempaquetar cadenas de bytes
from struct import pack
import thread
from hashBuffer import HashBuffer

class Peer:
    def __init__(self):
        self.MSGLEN = 1026
        
        self.direcPeers = []
        
        self.socketUDP = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.socketPerdidosUDP = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.socketPerdidosUDP.bind(('', 0))#Puero 0 = el sistema operativo elige uno libre
        #self.puerto = self.socketUDP.getsockname()[1]
        print "SocketUDP enlazado"
        
        self.socketSourceTCP = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
        
        self.socketPlayerTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Socket que espera conexion VLC
        self.socketPlayerTCP.bind(('', 0)) 

        self.socketPlayerTCP.listen(1)
        self.direccionPlayer = '' #(ip, puerto) de haber hecho accept
        self.socketClientePlayer = None #Socket para comunicarse con VLC, repuesta al hacer accept con socketPlayerTCP
        
        self.buffer = HashBuffer(512) 
        
    def aceptarConexionPlayerTCP(self):
        print "Esperando aceptar conexion TCP por parte del player VLC"
        thread.start_new(self.abrirVLC, ())
        (self.socketClientePlayer, self.direccionPlayer) = self.socketPlayerTCP.accept()
        print "Conexion con el player aceptada"
        print "Direccion player: ", self.direccionPlayer
        
    def conectarSourceTCP(self, ip, puerto):
        print "Esperando respuesta del servidor... "
        self.socketSourceTCP.connect((ip, puerto))
        self.socketUDP.bind(("",self.socketSourceTCP.getsockname()[1]))
        print "Conexion TCP establecida con ", (ip, puerto)
    
    #Recibe igual que el flujo UDP pero solo 10 veces y mediante el socketSourceTCP
    def recibirCabeceraOggTCP(self):
        i = 0
        cabecera = ''
        while i < 10:
            (msg,dir) = self.leerSocket(self.socketSourceTCP, self.MSGLEN-2)
            cabecera = cabecera + msg
            i += 1
            print "Recibido paquete de cabecera ", i
        return cabecera
    
    def bufferIn(self):
        i = 0
        while i<self.buffer.tam/2:
            (msg,dir) = self.leerSocket(self.socketUDP, self.MSGLEN) #Recibimos
            
            print "Bloque ", self.separarID(msg)[0],"de",dir," encolado"
            
            self.comprobarPaqueteDir(msg,dir)
            
            (id,msg)=self.separarID(msg)    #Separamos el numero de bloque del mensaje
            self.buffer.push(id, msg)   #"Encolamos"
            i+=1
    
    def comprobarPaqueteDir(self,paquete ,dir): #Comprueba si el paquete llega del source o de otro peer
            if dir == self.socketSourceTCP.getpeername(): #Si el paquete llega del source se reenvia
                self.reenviarPaqueteRestoPeers(paquete)
                dir = None
                
            if (dir != None) and (not self.buscarDirecPeer(dir)): #Si llega un paquete de un peer que no tenemos en la lista, append peer
                self.direcPeers.append(dir)
                
    def buscarDirecPeer(self, dir): #Busca un peer 
        for i in self.direcPeers:
            if dir == i:
                return True
        return False
        
    
    def reenviarPaqueteRestoPeers(self, paquete):
        for i in self.direcPeers:
            self.socketUDP.sendto(paquete,i)
        
            
    def separarID(self, msg):
        return (unpack(">H", msg[:2])[0], msg[2:])
        
        
    def leerSocket(self,socket,tam):
        msg = ''
        while len(msg) < tam:
            (chunk,dir) = socket.recvfrom(tam-len(msg)) 
            if chunk == '':
                print RuntimeError("socket connection broken flujo Ogg")
                
            
            msg = msg + chunk
        return (msg,dir)
    
    def recibirPeersConectados(self):
        recv = self.socketSourceTCP.recv(2)
        numConect = unpack(">H", recv)[0]
        i = 0
        
        
        ip = ""
        puerto = 0
        print "Peer conectado: ", numConect
        
        while i < numConect:
            (recv,dir) = self.leerSocket(self.socketSourceTCP, 12)
            j = 0
            while j < 4:
                ip += str(unpack(">H", recv[j*2:(j+1)*2])[0])+"."
                j += 1
            ip = ip[:-1]
            
            puerto = unpack(">I",recv[8:12])[0]
            
            self.direcPeers.append((ip,puerto))
            print (ip,puerto)
            ip = ""
            
            i += 1
            
            
    def recibirPaquetesPerdidos(self):
        print "Socket perdidos:",self.socketPerdidosUDP.getsockname()
        while True:
            leido = self.leerSocket(self.socketPerdidosUDP, self.MSGLEN) 
            (id,msg) = self.separarID(leido)
            print "Bloque perdido",id, "recibido"
            self.buffer.push(id, msg)   
        
    def recibirFlujoOggUDP(self):
        ruta = self.getEscritorio(self.escribirPorTeclado())
        f = open(ruta, "wb")
        i = 0
        
        print "Recibiendo lista de direcciones de peers conectados..."
        self.recibirPeersConectados()
        
        cabe = self.recibirCabeceraOggTCP()
        
        print "Encolando..."
        self.bufferIn()
        
        #sys.exit()
        
        while i < 10:
            self.socketClientePlayer.send(cabe[1024*i:1024*(i+1)])
            i += 1
        
        i = 0
        
        f.write(cabe)
        
        
        
        print "Cabecera Ogg escrita"
        while True:
            (msg,dir) = self.leerSocket(self.socketUDP, self.MSGLEN)
                        
            (numeroBloque, msg2) = self.separarID(msg);
            
            self.comprobarPaqueteDir(msg,dir)
            
            self.buffer.push(numeroBloque, msg2)
            
            self.comprobarPaquetePerdido()
            
            f.write(msg2)
            (id, pop) = self.buffer.pop()
            
            
            
            if pop == "":
                #print "Bloque nulo."
                continue
            
            self.socketClientePlayer.send(pop)
            i = i +1
            #print i, " Iteracion - ", id, " bloque leido";
            
            
    def comprobarPaquetePerdido(self):
        if(self.buffer.peekMiddle()[1] is None):
            #print "Bloque perdido",self.buffer.peekMiddle()[0],"pedido."
            num = pack(">H",self.buffer.peekMiddle()[0]%self.buffer.tam)
            self.socketUDP.sendto(num,self.socketSourceTCP.getpeername())
            
    
    #def recuperarPaquetePerdido(self):
        #while True:
            #self.socketUDP.recvfrom()
    
    def escribirPorTeclado(self):
        #return raw_input("Introduzca algo por teclado: ")
        return "bunny" #para no escribir todo el rato haciendo pruebas
    
    def getEscritorio(self, nombreArchivo):
        if(os.name == 'nt'): #Windows
            ruta = "C:\\Users\\" + getpass.getuser() + "\\Desktop\\" + nombreArchivo + ".ogg"
        else:
            ruta = "/home/" + getpass.getuser() + "/Escritorio/" + nombreArchivo + ".ogg"
        return ruta
    
    def abrirVLC(self):
        if(os.name == 'nt'): #Windows
            os.system('"C:\\Program Files (x86)\\VideoLAN\\vlc\\vlc" --verbose=-1 http://localhost:'+str(self.socketPlayerTCP.getsockname()[1]))
        else:
            os.system('vlc --verbose=-1 http://localhost:'+str(self.socketPlayerTCP.getsockname()[1]))
             
peer = Peer()
#peer = Peer('87.216.135.207', 12000)
peer.aceptarConexionPlayerTCP()
peer.conectarSourceTCP('localhost', 12000)
thread.start_new_thread(peer.recibirPaquetesPerdidos, ())
peer.recibirFlujoOggUDP()