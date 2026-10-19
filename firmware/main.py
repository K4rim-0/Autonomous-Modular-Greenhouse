from machine import Pin
import dht
import time



from rotaryEncoderClass import rotaryEncoderClass
from tempHumClass import tempHumClass
from oledClass import oledClass
from ledClass import ledClass
from LdrSoilClass import Soil, LDR
from servo import Servo

def timeout(time):
    if encoder.time_last_turn() > time:
        encoder.reset_time_last_turn()
        return True
    else:
        return False

def sleep(time):
    if encoder.time_last_turn() > time:
        return True
    else:
        return False

def bool_toString(boolean):
    if boolean:
        return "Enabled"
    else:
        return "Disabled"

sensor = dht.DHT22(Pin(3))
last_measure = time.ticks_ms()
switch = True
                            	#to time reading from sensors so not to waste energy on constant reading
update_screen = False			#to see when the screen needs an update, set to false unless conditions change to justify the need for refresh
                                #keep a False flager at end and set condition that would enable oled to update at start of code such that if a condition is
                                #met inside code like (encoder movement or click or time passed) and if statement for all menus for the update_screen bool
encoder_click_latch = False
encoder_turn_latch = False
update_screen_timeout = time.ticks_ms()
update_servo_latch = False
update_servo_timeout = time.ticks_ms()
check_servo_flag = False			#it will be used to see what the proper state of the servo should be (open or closed after adjustment or test) for activeAngle

servo_latch = time.ticks_ms()

led = ledClass()
encoder = rotaryEncoderClass()
oled = oledClass()
ldr = LDR()
soil = Soil()
servo = Servo(Pin(13))

def encoder_sense():
    global encoder_turn_latch, encoder_click_latch
    global encoder
    if encoder.direction() != 0:
        encoder_turn_latch = True
    if encoder.click():
        encoder_click_latch = True

temperature = tempHumClass(22, 38, 18, 1, "Temperature")

humidity = tempHumClass(45, 90, 30, 5, "Humidity")

matPin = Pin(6, Pin.OUT)
lightPin = Pin(7, Pin.OUT)

pumpPin = Pin(4, Pin.OUT)
fanPin = Pin(5, Pin.OUT)

matPin.value(1)
lightPin.value(1)               #default on on low voltage, need high to be off

mat_on = False
lamp_on = False
pump_on = False

oled_on = True
oled_awake = True

moisture_level = -1
light_level = -1

openAngle = 90
closeAngle = 90
activeAngle = 90
testAngle = 90

setLight = 50
setMoist = 50

fade_rate = 3

atomizer = Pin(14, Pin.OUT)

menu_names = ["Temperature", "Humidity", "Heat Mat", "Lamp", "Pump", "Moistrue", "Light Level", "Servo","Test"]

test_names=["Servo", "RGB", "Light", "Heat", "Fan", "Pump", "Atomizer", "Exit"]

servo_menu = ["Open Angle", "Close Angle", "Exit"]

rgb_menu = ["Red","Green", "Blue", "Exit"]

menu_position = 0
test_position = 0
servo_position = 0
rgb_position = 0

rTest = 0
gTest = 0
bTest = 0

active_menu = 0		#this is to decide on what menu to show in nonblocking menu system

pump_running = False
fan_running = False
atomizer_running = False
mat_running = False
light_running = False
screen_running = False
update_pass = False

led_tested = False
pump_tested = False
fan_tested = False
atomizer_tested = False
mat_tested = False
lamp_tested = False

pump_flag = False
fan_flag = False
atomizer_flag = False
mat_flag = False
lamp_flag = False

atomizer_active = False

last_soil_moisture_check = time.ticks_ms()
soil_moisture_interval = 3600 * 1000		#to see how long between soil moisture checks, set to 1hr
pump_run_time = time.ticks_ms()				#used to check how long the pump has run for
pump_active_time = 5*1000					#to determine for how long pump should run when activated 5000 ms = 5sec
pump_active = False

last_temperature_check = time.ticks_ms()
temperature_interval = 30*1000 			#every .5 minutes

last_humidity_check = time.ticks_ms()
humidity_interval = 1200 * 1000
atomizer_run_time = time.ticks_ms()
atomizer_active_time = 10*1000

last_light_check = time.ticks_ms()
light_interval = 20 * 1000
lamp_active = False

ldr_pause = time.ticks_ms()	#this is to give the ldr time to calibrate to ambient
ldr_wait = 10*1000			#light levels before making reading to decide to activate light
ldr_calibrate = False

led.off()

try:
    sensor.measure()
    temp_read = sensor.temperature()
    hum_read = sensor.humidity()
except:
    temp_read = -1
    hum_read = -1
    

while True:
    
    curr_time = time.ticks_ms()
    encoder_dir = encoder.direction()
    encoder_click = encoder.click()
    
    
       
    if encoder_dir != 0:
        encoder_turn_latch = True
    if encoder_click:
        encoder_click_latch = True
    
    if sleep(10*1000):
        if oled_awake:
            oled.off()
            oled_awake = False
        screen_running = False
        menu_position = 0
    else:
        if not oled_awake:
            oled.on()
            oled_awake = True
        if not led_tested:
            screen_running = True
        
    if time.ticks_diff(curr_time, servo_latch) < 400:
        servo.write(activeAngle)
    else:
        servo.off()
        check_servo_flag = False
    
    if time.ticks_diff(time.ticks_ms(), last_measure) > 5000:
        last_measure = time.ticks_ms()
        try:
            sensor.measure()
            hum_read = sensor.humidity()
            temp_read = sensor.temperature()
            moisture_level = 100 - int((soil.moisture_level() / 65535) * 100) #subtract reading from 100 to get 100% as wet and 0 % as dry
            light_level = int((ldr.light_level() / 65535) * 100)
            update_screen = True 
        except:
            hum_read = -1
            temp_read = -1
            light_level = -1
            moisture_level = -1
            
            
            
 #===================================== system control to opperate the peripheral systems (fan, pump, heatmat, light)
    
    # led to signal whats going on (blue = water, cyan = cooling, orange = heating,
    
    if led_tested:
        led.light_custom(rTest, gTest, bTest)
    elif pump_running:
        led.fade(0,0, 130, fade_rate)
    elif atomizer_running:
        led.fade(0,130,0, fade_rate)
    elif fan_running:
        led.fade(0, 130, 130, fade_rate)
    elif mat_running:
        led.fade(130, 65, 0, fade_rate)
    elif light_running:
        led.fade(130, 0, 130, fade_rate)
    elif screen_running:
        led.fade(130,130,130,fade_rate)
    else:
        led.off()
    
    
    # soil / pump
    if not pump_tested:
        
        if time.ticks_diff(curr_time, last_soil_moisture_check) > soil_moisture_interval and pump_on:
            last_soil_moisture_check = curr_time
            if (setMoist <= moisture_level - 10):
                pump_active = True
                pump_run_time = curr_time
                
        if (pump_active and time.ticks_diff(curr_time, pump_run_time) < pump_active_time):
            pumpPin.value(1)
            pump_running = True
            
        else:
            pump_running = False
            pumpPin.value(0)
    
    elif pump_tested:
        pumpPin.value(1)    

        
        
    # temperature fan / heat mat
    
    if check_servo_flag:
        check_servo_flag = False
        servo_latch = curr_time
        
        if temp_read >= int(temperature.get_set_val()) + 1:
            activeAngle = openAngle
            
        elif temp_read - 1 <= int(temperature.get_set_val()):
            activeAngle = closeAngle
        
        
    
    
    
    if not (mat_tested or fan_tested):
        if (time.ticks_diff(curr_time, last_temperature_check) > temperature_interval or check_servo_flag) and temperature.get_set_val() != "---":
            last_temperature_check = curr_time
            set_temp = int(temperature.get_set_val())
            check_servo_flag = False
            
            if temp_read >= set_temp + 2:
                mat_running = False
                activeAngle = openAngle
                fan_running = True
                fanPin.value(1)
                matPin.value(1)
            
            elif  temp_read >= set_temp + 1:
                mat_running = False
                fan_running = False
                activeAngle = openAngle
                fanPin.value(0)
                matPin.value(1)
            
            elif temp_read <= set_temp - 2:
                fan_running = False
                fanPin.value(0)
                activeAngle = closeAngle
                if mat_on:
                    matPin.value(0)			#mat pin and light pin work in reverse, 1 = off and 0 = on
                    mat_running = True
                elif not mat_on:
                    matPin.value(1)
                    mat_running = False
        
            elif temp_read - 1 <= set_temp:
                mat_running = False
                fan_running = False
                fanPin.value(0)
                activeAngle = closeAngle
                matPin.value(1)
                
        elif temperature.get_set_val() == "---":
            mat_running = False
            fan_running = False
            fanPin.value(0)
            matPin.value(1)
            
    elif fan_tested or mat_tested:
        if fan_tested:
            fanPin.value(1)
        else:
            matPin.value(0)
        
    #humidity / atomizer
    if not atomizer_tested:    
        if time.ticks_diff(curr_time, last_humidity_check) >= humidity_interval and humidity.get_set_val() != "---":
            last_humidity_check = curr_time
            atomizer_run_time = curr_time
            
            if hum_read < int(humidity.get_set_val()) - 5:
                atomizer_active = True
            else:
                atomizer_active = False
        
        
        if (time.ticks_diff(curr_time, atomizer_run_time) >= atomizer_active_time) or humidity.get_set_val() == "---":
            atomizer_active = False
        
        if atomizer_active:
            atomizer_running = True
            atomizer.value(1)
        elif not atomizer_active:
            atomizer_running = False
            atomizer.value(0)
    
    elif atomizer_tested:
         atomizer.value(1)   
        

        
        
    #light
    if not lamp_tested:
        if (time.ticks_diff(curr_time, last_light_check) > light_interval or lamp_flag) and lamp_on:
            last_light_check = curr_time
            lightPin.value(1)
            ldr_pause = curr_time
            ldr_calibrate = True
        
        if ldr_calibrate and time.ticks_diff(curr_time, ldr_pause) > ldr_wait:
            ldr_calibrate = False
            
            if light_level < setLight - 10:
                lamp_active = True
            else:
                light_running = False
                lamp_active = False
        
        if lamp_active:
            light_running = True
            lightPin.value(0)
        else:
            light_running = False
            lightPin.value(1)
            
    elif lamp_tested:
        lightPin.value(0)
        
            
            
            
            
    
#================================================Main menu========================================================    
    if encoder_turn_latch or encoder_click_latch or time.ticks_diff(curr_time, update_screen_timeout) > 2500:
        update_screen = True
        update_screen_timeout = curr_time
    
    
    if active_menu == 0:
        menu_position += encoder_dir
        
        if menu_position < 0 or menu_position > 8:
            if menu_position < 0:
                menu_position = 8
            else:
                menu_position = 0
            
        if update_screen:
            update_screen = False
            if menu_position < 4:
                temp_str = str("CT:" + "{:.1f}".format(temp_read) + "C ST:" + str(temperature.get_set_val()) + "C")
                hum_str = str("CH:" + "{:.1f}".format(hum_read) + "% SH:" + str(humidity.get_set_val()) + "%")
                mat_str = str("Mat: " + bool_toString(mat_on))
                lamp_str = str("Lamp: " + bool_toString(lamp_on))
                
                oled.print_menu(temp_str, hum_str, mat_str, lamp_str, menu_position, menu_names)
                
            elif (menu_position >= 4) and (menu_position < 8):
                pump_str = str("Pump: " + bool_toString(pump_on))
                moisture_str = str("CM:" + "{:.1f}".format(moisture_level) + "%" + " SM:" + str(setMoist) + "%")
                light_str = str("CL:" + "{:.1f}".format(light_level) + "%" + " SL:" + str(setLight) + "%")
                servo_str = str("Servo Trim")
                oled.print_menu(pump_str, moisture_str, light_str, servo_str, menu_position, menu_names)
            else:
                oled.print_menu("Test", "", "", "", menu_position, menu_names)
            
        if encoder_click_latch:
            active_menu = menu_position + 1
            originalAngle = activeAngle
            update_screen = True
            encoder_click_latch = False
    
    
#=================================================actions===========================================================        
    #time.sleep(0.05)   	#found adding a bit of a dellay helps in smoothing out the cycle
    
    if active_menu in range(1, 10):
        if active_menu == 1:
            
            temperature.adjust(encoder_dir)
            if update_screen:
                update_screen = False
                oled.special_range_menu(temperature.name, temperature.min_val, temperature.max_val, temperature.set_val, "C", temperature.account)
            if timeout(5000) or encoder_click_latch:
                active_menu = 0
                update_screen = True
                encoder_click_latch = False
        
        elif active_menu == 2:
            update_screen = False
            humidity.adjust(encoder_dir)
            if update_screen:
                oled.special_range_menu(humidity.name, humidity.min_val, humidity.max_val, humidity.set_val, "%", humidity.account)
            if timeout(5000) or encoder_click_latch:
                active_menu = 0
                update_screen = True
                encoder_click_latch = False
                
        elif active_menu == 3:
            
            if encoder_dir == 1:
                mat_on = True
            elif encoder_dir == -1:
                mat_on = False
                
            if update_screen:
                update_screen = False
                oled.bool_menu("Heat Mat", mat_on)
            
            if timeout(5000) or encoder_click_latch:
                active_menu = 0
                update_screen = True
                encoder_click_latch = False
                
        elif active_menu == 4:
            
            if encoder_dir == 1:
                lamp_on = True
            elif encoder_dir == -1:
                lamp_on = False
            
            if update_screen:
                update_screen = False
                oled.bool_menu("Grow Light", lamp_on)
            
            if timeout(5000) or encoder_click_latch:
                active_menu = 0
                update_screen = True
                encoder_click_latch = False
    
        elif active_menu == 5:
            
            if encoder_dir == 1:
                pump_on = True
            elif encoder_dir == -1:
                pump_on = False
                
            if update_screen:
                update_screen = False
                oled.bool_menu("Water Pump", pump_on)
            
            if timeout(5000) or encoder_click_latch:
                active_menu = 0
                update_screen = True
                encoder_click_latch = False
                
        elif active_menu == 6:
            
            setMoist += encoder_dir*5
            if setMoist < 0:
                setMoist = 0
            if setMoist > 100:
                setMoist = 100
                
            if update_screen:
                update_screen = False
                oled.special_range_menu("Soil Moisture", 0, 100, setMoist, "%", True)
            
            if timeout(5000) or encoder_click_latch:
                active_menu = 0
                update_screen = True
                encoder_click_latch = False
    
        elif active_menu == 7:
            
            setLight += encoder_dir*5
            if setLight < 0:
                setLight = 0
            if setLight > 100:
                setLight = 100
                
            if update_screen:
                update_screen = False
                oled.special_range_menu("Grow Light", 0, 100, setLight, "%", True)
            
            if timeout(5000) or encoder_click_latch:
                active_menu = 0
                update_screen = True
                encoder_click_latch = False
    
        elif active_menu == 8:
            
            servo_position += encoder_dir
            if servo_position < 0 or servo_position > 2:
                if servo_position < 0:
                    servo_position = 2
                else:
                    servo_position = 0
            
            
                
            open_str = str("Open: " + str(openAngle))
            close_str = str("Close: " + str(closeAngle))            
            
            if update_screen:
                update_screen = False
                oled.print_menu(open_str, close_str, "Exit", "", servo_position, servo_menu)
        
            if timeout(10000) or (encoder_click_latch and servo_position == 2):
                servo_position = 0 #0 this is for the servo menu position tracking and we reset it so that when we enter menu again we are at first option
                active_menu = 0
                update_screen = True
                encoder_click_latch = False
                servo_latch = curr_time
            elif encoder_click_latch:
                active_menu = servo_position+81
                update_screen = True
                encoder_click_latch = False
                
        elif active_menu == 9:
            
            test_position += encoder_dir
            
            if test_position < 0 or test_position > 7:
                if test_position < 0:
                    test_position = 7
                else:
                    test_position = 0
            
            if test_position < 4:
                if update_screen:
                    update_screen = False
                    oled.print_menu(test_names[0], test_names[1], test_names[2], test_names[3], test_position, test_names)
            else:
                if update_screen:
                    update_screen = False
                    oled.print_menu(test_names[4], test_names[5], test_names[6], test_names[7], test_position, test_names)
            
            
            if timeout(10000) or (encoder_click_latch and test_position == 7):
                test_position = 0
                active_menu = 0
                update_screen = True
                encoder_click_latch = False
                
            elif encoder_click_latch:
                originalAngle = activeAngle
                active_menu = test_position+91
                update_screen = True
                encoder_click_latch = False
        
    if active_menu in range(81,83):
        if active_menu == 81:
            
            openAngle += encoder_dir*5
            
            if openAngle > 180 or openAngle < 0:
                if openAngle > 180:
                    openAngle = 180
                else:
                    openAngle = 0
                            
            if update_screen:
                update_screen = False
                oled.special_range_menu("Open", 0, 180, openAngle, "", True)
            activeAngle = openAngle
            update_servo_latch = True
            servo_latch = curr_time
            
            if timeout(5000) or encoder_click_latch:
                servo_position = 0
                active_menu = 8
                update_screen = True
                servo_latch = curr_time
                encoder_click_latch = False
                servo.write(activeAngle)
                check_servo_condition = True
                check_servo_flag = True
        
        else:
            closeAngle += encoder_dir*5
                    
            if closeAngle > 180 or closeAngle < 0:
                if closeAngle > 180:
                    closeAngle = 180
                else:
                    closeAngle = 0
                            
            if update_screen:
                update_screen = False
                oled.special_range_menu("Closed", 0, 180, closeAngle, "", True)
            activeAngle = closeAngle
            update_servo_latch = True
            servo_latch = curr_time

            if timeout(5000) or encoder_click_latch:
                servo_position = 0
                active_menu = 8
                update_screen = True
                encoder_click_latch = False
                servo.write(activeAngle)
                check_servo_condition = True
                check_servo_flag = True
            
    if active_menu in range(91, 99):	#test_names=["Servo", "RGB", "Light", "Heat", "Fan", "Pump", "Atomizer", "Exit"]
        
        if active_menu == 91:
            testAngle += encoder_dir*5
            
            if testAngle > 180 or testAngle < 0:
                if testAngle > 180:
                    testAngle = 180
                else:
                    testAngle = 0
                            
            if update_screen:
                update_screen = False
                oled.special_range_menu("Test", 0, 180, testAngle, "", True)
            activeAngle = testAngle
            update_servo_latch = True
            servo_latch = curr_time
            
            if timeout(5000) or encoder_click_latch:
                test_angle = 90
                active_menu = 9
                activeAngle = originalAngle
                update_screen = True
                encoder_click_latch = False
                servo.write(activeAngle)
                check_servo_condition = True
                check_servo_flag = True
        
        elif active_menu == 92:
                    
            rgb_position = (rgb_position + encoder_dir) % 4
                    
            if update_screen:
                update_screen = False
                r_str = str("red: " +  str(rTest))
                g_str = str("green: " + str(gTest))
                b_str = str("blue: " + str(bTest))
            
                oled.print_menu(r_str, g_str, b_str, "Exit", rgb_position, rgb_menu)
                                
            if timeout(10000) or (encoder_click_latch and rgb_position == 3):
                rgb_position = 0
                active_menu = 9
                update_screen = True
                encoder_click_latch = False
                led_tested = False
                rTest = gTest = bTest = 0
                led.off()
            elif encoder_click_latch:
                led_tested = True
                active_menu = rgb_position+921
                update_screen = True
                encoder_click_latch = False
                    
                    
        elif active_menu == 93:
            
            if update_screen:
                update_screen = False
                oled.print_menu(test_names[0], test_names[1], str(test_names[2] + "(ON)"), test_names[3], test_position, test_names)
                    
            lightPin.value(0)
            lamp_tested = True
                
            if timeout(5000) or encoder_click_latch:
                lightPin.value(1)
                active_menu = 9
                lamp_tested = False
                update_screen = True
                encoder_click_latch = False
                
        elif active_menu == 94:
            
            if update_screen:
                update_screen = False
                oled.print_menu(test_names[0], test_names[1], str(test_names[2]), test_names[3] + "(ON)", test_position, test_names)
                    
            matPin.value(0)
            mat_tested = True
                
            if timeout(5000) or encoder_click_latch:
                matPin.value(1)
                mat_tested = False
                mat_flag = True
                active_menu = 9
                update_screen = True
                encoder_click_latch = False
        
        elif active_menu == 95:
                
            if update_screen:
                update_screen = False
                oled.print_menu(str(test_names[4] + "(ON)"), test_names[5], test_names[6], test_names[7], test_position, test_names)
            fanPin.value(1)
            fan_tested = True
            
            if timeout(5000) or encoder_click_latch:
                fanPin.value(0)
                fan_tested = False
                fan_flag = True
                active_menu = 9
                update_screen = True
                encoder_click_latch = False
                
        elif active_menu == 96:
            
            if update_screen:
                update_screen = False
                oled.print_menu(test_names[4],str(test_names[5] + "(ON)"), test_names[6], test_names[7], test_position, test_names)
            pumpPin.value(1)
            pump_tested = True
            
            if timeout(5000) or encoder_click_latch:
                pumpPin.value(0)
                pump_tested = False
                pump_flag = True
                active_menu = 9
                update_screen = True
                encoder_click_latch = False
                
        elif active_menu == 97:
            
            if update_screen:
                update_screen = False
                oled.print_menu(test_names[4], test_names[5], str(test_names[6] + "(ON)"), test_names[7], test_position, test_names)
            atomizer_tested = True
            
            if timeout(5000) or encoder_click_latch:
                atomizer.value(0)
                atomizer_tested = False
                active_menu = 9
                update_screen = True
                encoder_click_latch = False
            
    
    if active_menu in range(921, 924):
        
        if active_menu == 921:
            
            rTest += encoder_dir*10
                        
            if rTest < 0 or rTest > 250:
                if rTest < 0:
                    rTest = 0
                else:
                    rTest = 250
                        
            if update_screen:
                update_screen = False
                oled.special_range_menu("Red", 0, 250, rTest, "", True)
            led.light_custom(rTest, gTest, bTest)
            
            if timeout(5000) or encoder_click_latch:
                active_menu = 92
                update_screen = True
                encoder_click_latch = False
                
        elif active_menu == 922:
            gTest += encoder_dir*10
                        
            if gTest < 0 or gTest > 250:
                if gTest < 0:
                    gTest = 0
                else:
                    gTest = 250
                        
            if update_screen:
                update_screen = False
                oled.special_range_menu("Green", 0, 250, gTest, "", True)
            led.light_custom(rTest, gTest, bTest)
            
            if timeout(5000) or encoder_click_latch:
                active_menu = 92
                update_screen = True
                encoder_click_latch = False
        
        elif active_menu == 923:
            bTest += encoder_dir*10
                        
            if bTest < 0 or bTest > 250:
                if bTest < 0:
                    bTest = 0
                else:
                    bTest = 250
                        
            if update_screen:
                update_screen = False
                oled.special_range_menu("Blue", 0, 250, bTest, "", True)
            led.light_custom(rTest, gTest, bTest)
            
            if timeout(5000) or encoder_click_latch:
                active_menu = 92
                update_screen = True
                encoder_click_latch = False
                

    encoder_turn_latch = False









