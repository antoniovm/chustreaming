'''
Created on 15/03/2012

@author: jorge, antonio, miguel
'''
import socket
import getpass        
import os               #Para obtener datos del sistema operativo
from struct import unpack #Para desempaquetar cadenas de bytes
from struct import pack
import thread
from hashBuffer import HashBuffer
import IN
import subprocess



class Peer:
    def __init__(self):
        self.MSGLEN = 1026
        
        self.listaPeers = []
        
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
            self.buffer.push(id, (id,msg))   #"Encolamos"
            i+=1
    
    def comprobarPaqueteDir(self,paquete ,dir): #Comprueba si el paquete llega del source o de otro peer
            if dir == self.socketSourceTCP.getpeername(): #Si el paquete llega del source se reenvia
                self.reenviarPaqueteRestoPeers(paquete)
                dir = None
                
            if (dir != None) and (self.buscarDirecPeer(dir) < 0): #Si llega un paquete de un peer que no tenemos en la lista, append peer
                self.listaPeers.append((dir,0))
                
    def buscarDirecPeer(self, dir): #Busca un peer 
        j = 0
        for i in self.listaPeers:
            if dir == i[0]:
                return j
            j += 1
        return -1
        
    
    def reenviarPaqueteRestoPeers(self, paquete):
        for i in self.listaPeers:
            self.socketUDP.sendto(paquete,i[0])
        
            
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

        print "Peers conectados: ", numConect
        
        while i < numConect:
            bin = self.socketSourceTCP.recv(6)
            
            dir = self.desempaquetarDireccion(bin)
            
            self.listaPeers.append((dir,0))
            
            i += 1
            
    def empaquetarDireccion(self,(ip,puerto)):
        sep = ip.split(".")
        i = 0 
        binario = ''
        for i in sep:
            binario += pack(">b",int(i))
        
        binario += pack(">H",puerto)
        
        return binario   
            
    def desempaquetarDireccion(self,bin):
        ip = ""
        j = 0
        while j < 4:
            ip += str(unpack(">b", bin[j:(j+1)])[0])+"."
            j += 1
        ip = ip[:-1]
            
        puerto = unpack(">H",bin[4:6])[0]
        
        return (ip, puerto)
    
    
    def recibirPaquetesPerdidos(self):
        print "Socket perdidos:",self.socketPerdidosUDP.getsockname()
        while True:
            (leido,dir) = self.leerSocket(self.socketPerdidosUDP, self.MSGLEN) 
            (id,msg) = self.separarID(leido)
            print "Bloque perdido",id,"(indice buffer:",id%self.buffer.tam,")", "recibido"
            self.buffer.push(id, (id,msg))   
        
    def recibirFlujoOggUDP(self):
        #ruta = self.getEscritorio(self.escribirPorTeclado())
        #f = open(ruta, "wb")
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
        
        #f.write(cabe)
        
        
        
        print "Cabecera Ogg escrita"
        while True:
            (msg,dir) = self.leerSocket(self.socketUDP, self.MSGLEN)
                        
            (numeroBloque, msg2) = self.separarID(msg);
            
            self.comprobarPaqueteDir(msg,dir)
            
            self.comprobarGradoDeSolidaridad(dir)
            
            self.buffer.push(numeroBloque, (numeroBloque,msg2))
            
            self.comprobarPaquetePerdido()
            
            #f.write(msg2)
            leido = self.buffer.pop()
            
            
            if leido is None:       #Nos saltamos los bloques nulos
                continue
            
            
            
            (id, pop) = leido
            
            
            
            
            
            
            self.socketClientePlayer.send(pop)
            i = i +1
            #print i, " Iteracion - ", id, " bloque leido";
            
    
    def comprobarGradoDeSolidaridad(self,dir):
        indicePeer = self.buscarDirecPeer(dir)      #Buscamos el peer con esa direccion
        if indicePeer < 0:                          #Si no se ha encontrado
            return 
        
        (dir,gradoSolidaridad) = self.listaPeers[indicePeer]    #Extraemos su direccion y grado de solidaridad
        print "Grado de solidaridad de",dir,":",gradoSolidaridad
        self.listaPeers[indicePeer] = (dir,gradoSolidaridad+1)  #Incrementar grado de solidaridad
        
        if(gradoSolidaridad > 255):
            self.dividirGradosDeSolidaridad()                   #En caso de llegar a 256 se dividen toos los grados de solidaridad entre 2
    
    def dividirGradosDeSolidaridad(self):
        indicesAEliminar = []                                   #lista de indices de peers que se van a eliminar
        j = 0
        for (dir,gradoSolidaridad) in self.listaPeers:          #Recorrer la lista de peers dividiendo
            self.listaPeers[j]=(dir,gradoSolidaridad/2)
            if gradoSolidaridad/2 == 0:                         #En caso de ser cero, se incluye en la lista de peers que se van a eliminar
                indicesAEliminar.append(j)
            j +=1
        
        self.eliminarInsolidarios(indicesAEliminar)                             #Una vez recorrido, se eliminan los insolidarios, es decir los de grado igual a cero
            
            
    def eliminarInsolidarios(self,listaIndices):
        for i in listaIndices:
            print i[0],"eliminado."
            del self.listaPeers[i]
                
    def comprobarPaquetePerdido(self):
        if(self.buffer.peekMiddle()[1] is None):
            num = pack(">H",self.buffer.peekMiddle()[0]%self.buffer.tam)     #Numero de la posicion perdida
            #print "Bloque",self.buffer.peekMiddle()[0]%self.buffer.tam,"perdido."
            puerto = pack(">H", self.socketUDP.getsockname()[1])     #Paquete binario correspondiente al puerto del socket principal
            pkg = num + puerto
            self.socketPerdidosUDP.sendto(pkg,self.socketSourceTCP.getpeername())
            
    

        
        
    
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
            subprocess.call(['vlc',' --verbose=-1 http://localhost:'+str(self.socketPlayerTCP.getsockname()[1])])
            #os.system('"C:\\Program Files (x86)\\VideoLAN\\vlc\\vlc" --verbose=-1 http://localhost:'+str(self.socketPlayerTCP.getsockname()[1]))
        else:
            os.system('vlc --verbose=-1 http://localhost:'+str(self.socketPlayerTCP.getsockname()[1]))
             
peer = Peer()
#peer = Peer('87.216.135.207', 12000)
peer.aceptarConexionPlayerTCP()
peer.conectarSourceTCP('localhost', 12000)
thread.start_new_thread(peer.recibirPaquetesPerdidos, ())
peer.recibirFlujoOggUDP()