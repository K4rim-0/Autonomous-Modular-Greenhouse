import dht
from machine import Pin
import time
class tempHumClass():
    def __init__ (self,set_val, max_val, min_val, step, name):
        self.set_val = int(set_val)
        self.max_val = int(max_val)
        self.min_val = int(min_val)
        self.account = True
        self.step = int(step)
        self.name = name
        
    def get_set_val(self):
        if self.account:
            return str(self.set_val)
        else:
            return "---"
        
    def get_max_val(self):
        return int(self.max_val)
    
    def get_min_val(self):
        return int(self.min_val)
    
    def get_name(self):
        return str(name)
    
    def get_account(self):
        return self.account
    
    def set_new_val(self,new_val):
        self.set_val = int(new_val)
        
    def adjust(self, direction):
        if (self.set_val + self.step*direction < self.min_val) or (self.set_val + direction*self.step > self.max_val):
            self.set_val = self.set_val
            if direction == -1:
                self.account = False
        else:
            self.set_val += self.step*direction
            if not self.account and direction == 1:
                self.account = True 
        