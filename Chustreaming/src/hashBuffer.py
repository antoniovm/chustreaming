'''
Created on 28/03/2012

@author: jorge, antonio, miguel
'''

class hashBuffer:
    def __init__(self, tam):
        self.tam = tam
        self.buffer = [None] * tam
        self.num = 0
        self.cabeza = 0
        
    def push(self, id, msg):
        self.buffer[id%self.tam] = msg
        self.num += 1
        
    def pop(self):
        msg = self.buffer[self.cabeza%self.tam]
        self.buffer[self.cabeza%self.tam] = None
        self.num -= 1
        return msg
    
    
    
        
        
    