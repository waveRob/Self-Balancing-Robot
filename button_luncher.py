#!/usr/bin/env python3

import os
import time
import Adafruit_BBIO.GPIO as GPIO

BUTTON_PIN = "P8_9"   # PAUSE button
LED_PIN = "USR3"       # onboard LED

# Setup with pull-up resistor so input reads HIGH when idle
GPIO.setup(BUTTON_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(LED_PIN, GPIO.OUT)

print("Waiting for button press...")

led_state = False
last_blink = time.time()

while True:
    # Blink LED every 1 s to show ready state
    if time.time() - last_blink > 1:
        led_state = not led_state
        GPIO.output(LED_PIN, led_state)
        last_blink = time.time()

    # Check button press (active low)
    if GPIO.input(BUTTON_PIN) == 0:  # goes LOW when pressed
        print("Button pressed! Launching PID controller...")
        GPIO.output(LED_PIN, GPIO.HIGH)  # solid ON while running
        os.system("sudo python3 /var/lib/cloud9/project/pid_cntr.py")
        GPIO.output(LED_PIN, GPIO.LOW)   # turn off LED when done
        time.sleep(1)