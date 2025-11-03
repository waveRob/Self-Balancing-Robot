"""
Utiliy functions
"""

import math
from evdev import ecodes

def complementary_filter(filtered_angle, gx, ay, az, dt, Tf=0.02):
    alpha = Tf / (Tf + dt)
    acc_angle = -math.atan2(az, ay) * 180 / math.pi
    filtered_angle = alpha * (filtered_angle + (gx * dt)) + (1 - alpha) * acc_angle
    return filtered_angle
    
    
def joystick_thread(gamepad):
    global axis_x, axis_y, button_y
    for event in gamepad.read_loop():
        if event.type == ecodes.EV_ABS:
            if event.code == 1: axis_y = (event.value - 128) / 128.0
            elif event.code == 2: axis_x = (event.value - 128) / 128.0
        if event.type == ecodes.EV_KEY:
            if event.code == ecodes.BTN_WEST: button_y = bool(event.value)
                
            
