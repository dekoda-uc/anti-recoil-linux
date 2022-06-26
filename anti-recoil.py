import os
import time
import random
import keyboard
import mouse
from ctypes import *
libc = CDLL("libc.so.6")

# Requires sudo to run

# $ sudo pip install keyboard
# $ sudo pip install mouse
# $ sudo apt-get install python-ctypes

#
# FlowDistant@2022
#

class TimeVal(Structure):
    _fields_ = [("sec", c_long), ("u_sec", c_long)]

class InputEvent(Structure):
    _fields_ = [("time", TimeVal), ("type", c_uint16), ("code", c_uint16), ("value", c_int)]


class MouseInput:
    def __init__(self):
        self.handle = -1
        device_name = "event-mouse"
        for device in os.listdir("/dev/input/by-path/"):
            if device[-device_name.__len__():] == device_name:
                self.handle = os.open("/dev/input/by-path/" + device, os.O_WRONLY)
                return
        raise Exception("Input [" + device_name + "] not found!")

    def __del__(self):
        if self.handle != -1:
            os.close(self.handle)

    def __send_input(self, input_type, code, value):
        start = InputEvent()
        end = InputEvent()
        libc.gettimeofday(pointer(start.time), 0)
        start.type = input_type
        start.code = code
        start.value = value
        libc.gettimeofday(pointer(end.time), 0)
        libc.write(self.handle, pointer(start), sizeof(start))
        libc.write(self.handle, pointer(end), sizeof(end))

    def click(self):
        self.__send_input(0x01, 0x110, 1)
        libc.usleep(50000)
        self.__send_input(0x01, 0x110, 0)

    def move(self, x, y):
        self.__send_input(0x02, 0, x)
        self.__send_input(0x02, 1, y)      


# https://github.com/GoogleBhrome/Apex-Legends-Anti-Recoil
## Configuration
# Set the horizontal limit: 5 means a maximum of 5 pixels to the left or to the right every shot
horizontal_range = 2
# Set the minimum and maximum amount of pixels to move the mouse every shot
min_vertical = 1
max_vertical = 3
# Set the minimum and maximum amount of time in seconds to wait until moving the mouse again
min_firerate = 0.03
max_firerate = 0.04
# Set the toggle button
toggle_button = 'num lock'
# Set whether the anti-recoil is enabled by default
enabled = False

# Some prints for startup
print("Anti-recoil script started!")
if enabled:
    print("Currently ENABLED (Press NumLock to disable)")
else:
    print("Currently DISABLED (Press NumLock to enable)")

last_state = False

mouseIpt = MouseInput()

while True:
    key_down = keyboard.is_pressed(toggle_button)
    # If the toggle button is pressed, toggle the enabled value and print
    if key_down != last_state:
        last_state = key_down
        if last_state:
            enabled = not enabled
            if enabled:
                print("Anti-recoil ENABLED")
            else:
                print("Anti-recoil DISABLED")
    
    if mouse.is_pressed(button='left') and enabled:
        # Offsets are generated every shot between the min and max config settings
        offset_const = 1000
        horizontal_offset = random.randrange(-horizontal_range * offset_const, horizontal_range * offset_const, 1) / offset_const
        vertical_offset = random.randrange(min_vertical * offset_const, max_vertical * offset_const, 1) / offset_const

        # Move the mouse with these offsets 
        mouseIpt.move(int(horizontal_offset), int(vertical_offset))

        # Generate random time offset with the config settings
        time_offset = random.randrange(min_firerate * offset_const, max_firerate * offset_const, 1) / offset_const
        time.sleep(time_offset)
    # Delay for the while loop
    time.sleep(0.001)

