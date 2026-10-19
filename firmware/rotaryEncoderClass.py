from machine import Pin
import time
from rotary_irq_rp2 import RotaryIRQ


class rotaryEncoderClass():

    def __init__(self):
        self.SW = Pin(9, Pin.IN, Pin.PULL_UP)
        self.rotary_encoder = RotaryIRQ(pin_num_clk=11,
                                        pin_num_dt=10,
                                        min_val=0,
                                        reverse=False,
                                        range_mode=RotaryIRQ.RANGE_UNBOUNDED)

        self.val_old = 0
        self.last_turn = time.ticks_ms()

        self.sw_last = False
        self.sw_time = time.ticks_ms()

    def time_last_turn(self):
        return time.ticks_diff(time.ticks_ms(), self.last_turn)

    def reset_time_last_turn(self):
        self.last_turn = time.ticks_ms()

    def direction(self):
        val_new = self.rotary_encoder.value()
        diff = self.val_old - val_new        # existing sign convention
        if diff:
            self.val_old = val_new
            self.last_turn = time.ticks_ms()

            if diff > 4:
                diff = 4
            elif diff < -4:
                diff = -4
        return diff

    def click(self):
        curr_time = time.ticks_ms()
        pressed = self.SW.value() == 0
        if pressed and not self.sw_last and time.ticks_diff(curr_time, self.sw_time) > 200:
            self.sw_time = curr_time
            self.sw_last = True
            return True
        if not pressed:
            self.sw_last = False
        return False