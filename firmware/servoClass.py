from servo import Servo
import time

class servoClass():
    def __init__(self, pin):
        self.servo_control = Servo(pin)
        
        self.time = 0
        
    def set_angle(self, angle):
        self.time = time.time()
        self.servo_control.write(angle)
        
    def off(self):
        self.servo_control.off()