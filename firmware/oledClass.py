from lib import ssd1306
from machine import Pin, I2C, PWM, ADC 

class oledClass():
    
    def __init__(self):
        self.i2c = I2C(0,sda=Pin(0), scl=Pin(1), freq=400000) #freq must be 400000
        self.oled = ssd1306.SSD1306_I2C(128, 64, self.i2c)
    
    def print_menu (self, first, second, third, fourth, line, names):
        titles = names
        
        self.oled.fill(0)
        pointer = line % 4
        self.oled.text(">", 0, int(pointer*12 + 12))
        self.oled.text(titles[int(line)], 10, 0, 1)
        self.oled.text(first, 10, 12,1)
        self.oled.text(second, 10, 24, 1)
        self.oled.text(third, 10, 36, 1)
        self.oled.text(fourth, 10, 48, 1)
        self.oled.show()
    
    def off(self):
        self.oled.poweroff()
    
    def on(self):
        self.oled.poweron()
        
        
    def special_range_menu(self, name, min_val, max_val, val, unit, account):
        self.oled.fill(0)
        self.oled.text(name, 0, 0, 1)
        if account:
            string = str(str(val) + " " + unit)
        else:
            string = "---"
        
        self.oled.text(str(min_val), 0, 34, 1)
        self.oled.text(str(max_val), 106, 34, 1)
        self.oled.text(string, 50, 34, 1)
        
        self.oled.text("Min", 0, 24, 1)
        self.oled.text("Max", 104, 24, 1)
        if account:
            self.oled.text("Set", 54, 24, 1)
        else:
            self.oled.text("Dis", 54, 24, 1)
            
        rect = int(((val - min_val)/(max_val - min_val))*122)
        self.oled.rect(0, 50, 128, 11, 1)
        self.oled.fill_rect(3, 53, rect, 5, 1)
        
        self.oled.show()
        
    def bool_menu(self, name, state):
        self.oled.fill(0)
        self.oled.text(name, 0, 0, 1)
        if state:
            self.oled.text("ON", 56, 25, 1)
            self.oled.rect(0, 35, 128, 11, 1)
            self.oled.fill_rect(3, 38, 122, 5, 1)
            
        else:
            self.oled.text("OFF", 54, 25, 1)
            self.oled.rect(0, 35, 128, 11, 1)
        
        self.oled.show()
        
        
