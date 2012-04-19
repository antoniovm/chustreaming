'''
Created on 28/03/2012

@author: jorge, antonio, miguel
'''

class HashBuffer:
    def __init__(self, tam):
        self.tam = tam
        self.buffer = [None] * tam
        self.num = 0
        self.cola = -1
        self.buffering =False   
        
    def push(self, id, msg):
        if self.cola == -1:
            self.cola = id%self.tam 
        self.buffer[id%self.tam] = (id,msg)
        if msg == "":
            print id
        self.num = min((self.num+1,self.tam)) 
        
    def pop(self):
        if self.buffer[self.cola%self.tam] is None:
            return (-1,"")
        (id,msg) = self.buffer[self.cola%self.tam]
        self.buffer[self.cola%self.tam] = None
        self.cola = (self.cola+1)%self.tam
        if msg == None:
            return (-1,"")
        self.num -= 1
        return (id,msg)
    
    def peekMiddle(self):
        return ((self.tam/4+self.cola)%self.tam,self.buffer[(self.tam/4+self.cola)%self.tam])
        
        
    
    def pop2(self):
        while self.buffer[self.cola%self.tam] == None:
            self.cola = (self.cola+1)%self.tam
        msg = self.buffer[self.cola%self.tam]
        self.buffer[self.cola%self.tam] = None
        self.cola = (self.cola+1)%self.tam
        if msg == None:
            return (self.cola,"")
        self.num -= 1
        return (self.cola,msg)
    
    def buffering(self, booleano):
        self.buffer = booleano
        
    def index(self, i):
        if i>=self.tam:
            raise IndexError()
        return self.buffer[i]
    
    
    
        
        
    