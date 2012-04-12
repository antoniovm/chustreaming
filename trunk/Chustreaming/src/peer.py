'''
Created on 15/03/2012

@author: jorge, antonio, miguel
'''
import socket
import getpass          
import os               #Para obtener datos del sistema operativo
from struct import unpack #Para desempaquetar cadenas de bytes
from logging import thread
from hashBuffer import HashBuffer

class Peer:
    def __init__(self, ip, puerto):
        self.MSGLEN = 1026
          
        self.UDP_PORT=puerto
        self.socketUDP = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.socketUDP.bind( ('', self.UDP_PORT) )
        print "SocketUDP enlazado"
        
        self.TCP_IP=ip
        self.TCP_PORT=puerto
        self.socketSourceTCP = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
        
        self.PLAYER_PORT=12001
        self.socketPlayerTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Socket que espera conexion VLC
        self.socketPlayerTCP.bind(('', self.PLAYER_PORT))
        self.socketPlayerTCP.listen(1)
        self.direccionPlayer = '' #(ip, puerto) de haber hecho accept
        self.socketClientePlayer = None #Socket para comunicarse con VLC, repuesta al hacer accept con socketPlayerTCP
        
        self.buffer = HashBuffer(512) 
        
    def aceptarConexionPlayerTCP(self):
        print "Esperando aceptar conexion TCP por parte del player VLC"
        #thread.start_new(self.abrirVLC, ())
        (self.socketClientePlayer, self.direccionPlayer) = self.socketPlayerTCP.accept()
        print "Conexion con el player aceptada"
        print "Direccion player: ", self.direccionPlayer
        
    def conectarSourceTCP(self):
        print "Esperando respuesta del servidor... "
        self.socketSourceTCP.connect((self.TCP_IP, self.TCP_PORT))
        print "Conexion TCP establecida con ", self.TCP_IP
    
    #Recibe igual que el flujo UDP pero solo 10 veces y mediante el socketSourceTCP
    def recibirCabeceraOggTCP(self):
        i = 0
        cabecera = ''
        while i < 10:
            msg = self.leerSocket(self.socketSourceTCP, self.MSGLEN-2)
            cabecera = cabecera + msg
            i += 1
            print "Recibido paquete de cabecera ", i
        return cabecera
    
    def bufferIn(self):
        i = 0
        while i<256:
            msg = self.leerSocket(self.socketUDP, self.MSGLEN) #Recibimos
            (id,msg)=self.separarID(msg)    #Separamos el numero de bloque del mensaje
            self.buffer.push(id, msg)   #"Encolamos"
            i+=1
            
    def separarID(self, msg):
        return (unpack(">H", msg[:2])[0], msg[2:])
        
        
    def leerSocket(self,socket,tam):
        msg = ''
        while len(msg) < tam:
            chunk = socket.recv(tam-len(msg)) 
            if chunk == '':
                #print RuntimeError("socket connection broken flujo Ogg")
                continue
            
            msg = msg + chunk
        return msg
        
    def recibirFlujoOggUDP(self):
        ruta = self.getEscritorio(self.escribirPorTeclado())
        f = open(ruta, "w")
        i = 0
        
        cabe = self.recibirCabeceraOggTCP()
        
        print "Encolando..."
        self.bufferIn()
        
        while i < 10:
            self.socketClientePlayer.send(cabe[1024*i:1024*(i+1)])
            i += 1
        
        i = 0
        
        f.write(cabe)
        
        
        
        print "Cabecera Ogg escrita"
        while True:
            msg = self.leerSocket(self.socketUDP, self.MSGLEN)
                        
            (numeroBloque, msg2) = self.separarID(msg);
            
            self.buffer.push(numeroBloque, msg2)
            
            f.write(msg2)
            pop = self.buffer.pop()
            if pop == "":
                continue
            self.socketClientePlayer.send(pop)
            i = i +1
            print i, " Iteracion - ", numeroBloque, " bloque obtenido";
            
            
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
            os.system('"C:\\Program Files (x86)\\VideoLAN\\vlc\\vlc" http://localhost:'+self.PLAYER_PORT)
        else:
            os.system('vlc http://localhost:'+self.PLAYER_PORT)
             
peer = Peer('localhost', 12000)
#peer = Peer('87.216.135.207', 12000)
peer.aceptarConexionPlayerTCP()
peer.conectarSourceTCP()
peer.recibirFlujoOggUDP()