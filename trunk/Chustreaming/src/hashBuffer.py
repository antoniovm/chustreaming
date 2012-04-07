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
            self.cola = id 
        self.buffer[id%self.tam] = msg
        self.num = min((self.num+1,self.tam))
        
    def pop(self):
        msg = self.buffer[self.cola%self.tam]
        self.buffer[self.cola%self.tam] = None
        self.cola = (self.cola+1)%self.tam
        self.num -= 1
        if msg == None:
            return ""
        return msg
    
    def buffering(self, booleano):
        self.buffer = booleano
    
    
    
        
        
    