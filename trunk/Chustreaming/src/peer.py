'''
Created on 15/03/2012

@author: jorge, antonio, miguel
'''
import socket
import getpass          
import os               #Para obtener datos del sistema operativo
from struct import unpack #Para desempaquetar cadenas de bytes

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
        
        self.socketPlayerTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #Socket que espera conexion VLC
        self.socketPlayerTCP.bind(('', 12001))
        self.socketPlayerTCP.listen(1)
        self.direccionPlayer = '' #(ip, puerto) de haber hecho accept
        self.socketClientePlayer = None #Socket para comunicarse con VLC, repuesta al hacer accept con socketPlayerTCP
        
    def aceptarConexionPlayerTCP(self):
        print "Esperando aceptar conexion TCP por parte del player VLC"
        (self.socketClientePlayer, self.direccionPlayer) = self.socketPlayerTCP.accept()
        print "Conexion con el player aceptada"
        print "Direccion player: ", self.direccionPlayer
        
    def conectarSourceTCP(self):
        self.socketSourceTCP.connect((self.TCP_IP, self.TCP_PORT))
        print "Conexion TCP establecida con ", self.TCP_IP
    
    #Recibe igual que el flujo UDP pero solo 10 veces y mediante el socketSourceTCP
    def recibirCabeceraOggTCP(self):
        i = 0
        cabecera = ''
        while i < 10:
            msg = ''
            while len(msg) < self.MSGLEN-2:
                chunk = self.socketSourceTCP.recv(self.MSGLEN-2-len(msg))
                if chunk == '':
                    print RuntimeError("socket connection broken cabecera TCP")
                    continue
                msg = msg + chunk
            cabecera = cabecera + msg
            i += 1
            print "Vuelta Peer ", i
        return cabecera
    
    def recibirFlujoOggUDP(self):
        ruta = self.getEscritorio(self.escribirPorTeclado())
        f = open(ruta, "w")
        i = 0
        
        cabe = self.recibirCabeceraOggTCP()
        
        while i < 10:
            self.socketClientePlayer.send(cabe[1024*i:1024*(i+1)])
            i += 1
        
        i = 0
        
        f.write(cabe)
        print "Cabecera Ogg escrita"
        while True:
            msg = ''
            while len(msg) < self.MSGLEN:
                chunk = self.socketUDP.recv(self.MSGLEN-len(msg)) 
                if chunk == '':
                    print RuntimeError("socket connection broken flujo Ogg")
                    continue
                
                msg = msg + chunk
                #print "received message:", msg
            
            numeroBloque=0
            numeroBloque=unpack(">H", msg[:2])[0] #Seleccionamos los 2 primeros bytes
            f.write(msg[2:])                       #Escribimos el resto en el fichero
            msg2 = msg[2:]
            self.socketClientePlayer.send(msg2)
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
    

peer = Peer('localhost', 12000)
peer.aceptarConexionPlayerTCP()
peer.conectarSourceTCP()
peer.recibirFlujoOggUDP()