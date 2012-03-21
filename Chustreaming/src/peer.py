'''
Created on 15/03/2012

@author: jorge, antonio, miguel
'''
import socket
import getpass          
import os               #Para obtener datos del sistema operativo
from struct import unpack #Para desempaquetar cadenas de bytes

class peer:
    def __init__(self, ip, puerto):
        self.MSGLEN = 1026
        self.numeroBloque=0;
          
        self.UDP_PORT=puerto
        self.socketUDP = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.socketUDP.bind( ('', self.UDP_PORT) )
        
        self.TCP_IP=ip
        self.TCP_PORT=puerto
        self.socketTCP = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
        
    def conectarTCP(self):
        self.socketTCP.connect(self.TCP_IP, self.TCP_PORT)
        print "Conexion TCP establecida con ", self.TCP_IP
    
    def recibirCabeceraOggTCP(self):
        i = 0
        cabecera = ''
        while i < 10:
            msg = ''
            while len(msg) < self.MSGLEN:
                chunk = self.socketTCP.recv(self.MSGLEN-len(msg)) 
                if chunk == '':
                    print RuntimeError("socket connection broken")
                    continue
                msg = msg + chunk
            cabecera = cabecera + msg
        return cabecera
    
    def recibirFlujoOggUDP(self):
        ruta = self.getEscritorio(self.escribirPorTeclado())
        f = open(ruta, "w")
        i = 0
        while True:
            msg = ''
            while len(msg) < self.MSGLEN:
                chunk = self.socketUDP.recv(self.MSGLEN-len(msg)) 
                if chunk == '':
                    print RuntimeError("socket connection broken")
                    continue
                
                msg = msg + chunk
                #print "received message:", msg
            
            numeroBloque=unpack(">H", msg[:2])[0] #Seleccionamos los 2 primeros bytes
            f.write(msg[2:]);                       #Escribimos el resto en el fichero
            i = i +1
            print i, " Iteracion - ", numeroBloque, " bloque obtenido";
            
            
    def escribirPorTeclado(self):
        return raw_input("Introduzca algo por teclado: ")
    
    def getEscritorio(self, nombreArchivo):
        if(os.name == 'nt'): #Windows
            ruta = "C:\\Users\\" + getpass.getuser() + "\\Desktop\\" + nombreArchivo + ".ogg"
        else:
            ruta = "/home/" + getpass.getuser() + "/Escritorio/" + nombreArchivo + ".ogg"
        return ruta