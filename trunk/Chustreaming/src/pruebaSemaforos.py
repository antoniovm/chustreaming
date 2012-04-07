'''
Created on 28/03/2012

@author: Jorge
'''
from threading import Semaphore
from threading import Thread
import thread
import time


class HashBuffer:
    def __init__(self, tam):
        self.tam = tam
        self.buffer = [None] * tam
        self.num = 0
        self.cola = 0
        self.empezarLeer = Semaphore(0)
        
        self.elementoDisponible = Semaphore(0) #0
        self.espacioLibre = Semaphore(self.tam*2) #self.tam
        self.exmut = Semaphore(1)
        
    def push(self, id, msg):
        self.espacioLibre.acquire()
        self.exmut.acquire()
        self.buffer[id%self.tam] = msg
        self.num += 1
        print "Push ", id
        self.exmut.release()
        self.elementoDisponible.release()
        #time.sleep(10)
        
    def pop(self):
        self.elementoDisponible.acquire()
        self.exmut.acquire()
        msg = self.buffer[self.cola%self.tam]
        self.buffer[self.cola%self.tam] = None
        self.cola += 1
        self.cola = self.cola%self.tam
        self.num -= 1
        print "Pop ", msg 
        self.exmut.release()
        self.espacioLibre.release()
        return msg      

hashBuffer = HashBuffer(512)

def insertarDiez():
    i = 0
    while i < 10:
        hashBuffer.push(i, i)
        #print "Push ", i
        i += 1
        
def leerDiez():
    i = 0
    while i < 10:
        #print "Pop ", hashBuffer.pop()
        hashBuffer.pop()
        i += 1


class HiloInsertar(Thread):
    def __init__(self, hashBuffer):
        Thread.__init__(self)
        self.hashBuffer = hashBuffer
        
    def insertarDiez(self):
        i = 0
        while i < 65536:
            self.hashBuffer.push(i, i)
            i += 1
    
    def run(self):
        self.insertarDiez()

class HiloLeer(Thread):
    def __init__(self, hashBuffer):
        Thread.__init__(self)
        self.hashBuffer = hashBuffer
        
    def leerDiez(self):
        i = 0
        while i < 65536:
            hashBuffer.pop()
            i += 1
    
    def run(self):
        self.leerDiez()    

hiloInsertar = HiloInsertar(hashBuffer)
hiloLeer = HiloLeer(hashBuffer)

hiloLeer.start()
hiloInsertar.start()

#thread.start_new_thread(leerDiez,())
#insertarDiez()
#thread.start_new_thread(insertarDiez())