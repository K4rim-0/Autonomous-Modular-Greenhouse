from machine import ADC, Pin



class LDR():
    def __init__ (self):
        self.ldr = ADC(Pin(27, Pin.IN, Pin.PULL_DOWN))
        
    def light_level(self):
        return self.ldr.read_u16()
    
    def light_level_100(self):
        return int(self.ldr.read_u16() / 65536) * 100
        
class Soil():
    def __init__(self):
        self.soil = ADC(Pin(26, Pin.IN, Pin.PULL_DOWN))  #the pin 28 got BRICKED, change the solder job!
    
    def moisture_level(self):
        return self.soil.read_u16()
    
    def moisture_level_100(self):
        return int(self.soil.read_u16() / 65535) * 100
    
    
