import neopixel, machine
import time

class ledClass():
    def __init__(self):
        self.led = neopixel.NeoPixel(machine.Pin(12), 1)
        self.time = time.ticks_ms()
        self.reverse = False
        self.multiplier = 0
    
    def light_green(self):
        self.led[0]  = (0,255,0)
        self.led.write()
        
    def light_custom(self, red, green, blue):
        self.led[0] = (red, green, blue)
        self.led.write()
        
    def off(self):
        self.led[0] = (0,0,0)
        self.led.write()
        
    def fade(self, red, green, blue, pace):
        
        
        
        if time.ticks_diff(time.ticks_ms(), self.time) >= pace*10:
            
            gamma = (self.multiplier/255) ** 2
            
            
            r=int(red * gamma)
            g=int(green * gamma)
            b=int(blue * gamma)
            
            self.led[0] = (r,g,b)
            self.led.write()
            
            if not self.reverse:
                self.multiplier += 2
                if self.multiplier >= max(red,green,blue):
                    self.multiplier = max(red,green,blue)
                    self.reverse = True
            else:
                self.multiplier -= 2
                if self.multiplier <= 40:
                    self.multiplier = 40
                    self.reverse = False
            
            self.time = time.ticks_ms()