'''
Created on 06/03/2012

@author: jorge, antonio, miguel
'''

import socket
import thread
from struct import pack
from struct import unpack
from hashBuffer import HashBuffer


class NodoFuente:
    def __init__(self):
        self.MSGLEN = 1024
        
        self.PUERTO_POR_DEFECTO = 12000
        
        self.direcPeers = []
        self.indiceDirec = 0
        
        self.cabecera = ""
        self.socketIcecast = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socketIcecast.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)#Para evitar la excepcion de puerto en uso 
        
        self.socketServerTCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #socket TCP cabecera Ogg
        self.socketClientesUDP = socket.socket( socket.AF_INET, socket.SOCK_DGRAM )
        self.socketClientesUDP.bind(('', self.PUERTO_POR_DEFECTO ))
        
        self.socketServerTCP.bind(('', self.PUERTO_POR_DEFECTO ))
        self.socketServerTCP.listen(256)
        
        self.buffer = HashBuffer(512)
    def conectarIcecast(self):
        self.socketIcecast.connect(('localhost', 8000))
        self.socketIcecast.send("GET /canal1 HTTP/1.1\r\n\r\n")
        print "Conexion establecida con Icecast."
        
    def getPaquete(self, i):
        return self.cabecera[1024*i:1024*(i+1)];
        
    def aceptarConexionTCP(self):
        print "Esperando nueva conexion peer"
        nuevoSocketDir = self.socketServerTCP.accept()
        print "Nueva conexion aceptada"
        print "Direccion del nuevo peer: ", nuevoSocketDir[1]
        return nuevoSocketDir
    
    
    def enviarCabeceraPeer(self, socketTCP):
        print "Enviando cabecera..."
        
        i=0
        
        while i < 10:
            socketTCP.send(self.getPaquete(i))
            print "Paquete ", i, " enviado."
            i += 1
        print "Cabecera enviada."            
    
    def gestionarNuevoPeerConectado(self):
        nuevoSocketDir = self.aceptarConexionTCP()      #Aceptar nueva conexion
            
        self.enviarPeersActuales(nuevoSocketDir[0])     #Enviar la lista de peers conectados a traves del peurto TCP
        
        self.direcPeers.append(nuevoSocketDir[1])       #Agregamos solo la direccion del peer (para usarla como direccion UDP)
        
        self.enviarCabeceraPeer(nuevoSocketDir[0])      #Usamos el puerto TCP para enviar la cabecera
                
    def esperarNuevasConexiones(self):
        while True:
                self.gestionarNuevoPeerConectado()
            
           
        
    def enviarPeersActuales(self, socketPeer):      
        tamBinario = pack(">H",len(self.direcPeers))    #Enviamos el numero de peers que hay conectados
        print "Enviando numero de peers conectados (",len(self.direcPeers),")"
        socketPeer.send(tamBinario)
        print "Enviando direcciones de peers conectados"
        for i in self.direcPeers:
            print i
            binario = self.empaquetarDireccion(i) #Convertimos la direccion en una cadena binaria para ue sea de longitud fija
            print len(binario)
            socketPeer.send(binario)
                  
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
                
            self.cabecera += msg
            i += 1
            print "Recibido bloque ", i
        #f.close()
        

    def reenvioPaquetePerdido(self):
        while True:
            (pkg,dirSolic) = self.socketClientesUDP.recvfrom(8)#Recibimos el numero de posicion perdido
            num = unpack(">H",pkg[:2])[0]
            
            dirPrincipalSolic = self.desempaquetarDireccion(pkg[2:])        #Recibimos la direccion principal para comprobar si es un bloque suyo
            
            #print "Peticion del paquete",num, "de", dirSolic
            (dirRemitente,(numB,msg),contador) = self.buffer.index(num) #Leemos el conjunto de datos asociado al peer al que fue enviado el bloque pedido
            
            if dirPrincipalSolic != dirRemitente:   #Si las direcciones son iguales, se ignora la queja
                tupla = self.comprobarQuejas((dirRemitente,(numB,msg),contador))#Comprobamos el numero de quejas del rest de peers
                self.buffer.push(num, tupla)#Reinsertamos la tupla con los valores comprobados
            
            
            
            pkg = pack(">H",numB) + msg
            self.socketClientesUDP.sendto(pkg,dirSolic)#Reenviamos el paquete pedido
        
        
        
        
        
    def comprobarQuejas(self,tupla):
        (dir,pkg,contador) = tupla
        if(contador == -1): #El peer ya ha sido eliminado de la lista     
            return tupla
        contador += 1
        if(contador >= len(self.direcPeers)/2): #Si mas de la mitad de los peers se han quejado, lo eliminamos de la lista
            contador = -1
            try:
                self.direcPeers.remove(dir)
                print "Eliminado peer",dir,". Num peers:",len(self.direcPeers)
            except:
                print "",#El peer ya ha sido eliminado
        tupla = (dir,pkg,contador)
        return tupla
        
        
        
    
    def hiloLeerIcecast(self):
        numeroBloque = 0;
        #f = open("C:\\Users\\" + "Loop" + "\\Desktop\\" + "serverBunny" + ".ogg", "a")
        while True:
            msg = ''
            while len(msg) < self.MSGLEN:
                chunk = self.socketIcecast.recv(self.MSGLEN-len(msg))
                
                if chunk == '':
                    continue
                    #raise RuntimeError("socket connection broken icecast")
                    
                msg = msg + chunk
                
        
            
            
            if len(self.direcPeers) > 0:
                numeroBloque=(numeroBloque+1)%(2**16)
                
                try:
                    tupla = (self.direcPeers[self.indiceDirec],(numeroBloque,msg),-10) #-----------((ip,puerto),(numeroBloque,bloque),contadorQuejas)
                except:
                    self.indiceDirec = -1   #Evitar semaforos en la eliminacion concurrente de peers
                self.buffer.push(numeroBloque, tupla)
                
                binario = pack(">H", numeroBloque) #Codificado como short big-endian
                msg = binario + msg
                try:
                    self.socketClientesUDP.sendto(msg, (self.direcPeers[self.indiceDirec]))
                except:
                    self.indiceDirec = -1   #Evitar semaforos en la eliminacion concurrente de peers
                #print numeroBloque, " bloque enviado a ",self.direcPeers[self.indiceDirec] #Para mostrar cuantos bloques de bytes vamos leyendo
                self.indiceDirec = (self.indiceDirec + 1) % len(self.direcPeers) #A cada vuelta, mandamos a un peer distinto
            

nodoFuente = NodoFuente()
nodoFuente.conectarIcecast()
nodoFuente.recibirCabecera()
#nodoFuente.gestionarNuevoPeerConectado()    #Para esperar al primer peer
thread.start_new_thread(nodoFuente.esperarNuevasConexiones,())      #Esperar al resto de peers
thread.start_new_thread(nodoFuente.reenvioPaquetePerdido,())
nodoFuente.hiloLeerIcecast()

        