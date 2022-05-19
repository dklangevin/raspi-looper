import RPi.GPIO as gpio
import time
import readchar
import signal
import sys

def signal_handler(sig, frame):
    gpio.cleanup()
    sys.exit(0)

def button_pressed_callback(channel):
    print(f'Button {BUTTON_PINS[channel]} pressed!')

def setup_gpio(callback):
    BUTTON_PINS = {
        31: 1,
        33: 2,
        35: 3,
        37: 4
    }

    gpio.setmode(gpio.BOARD)

    for pin, _ in BUTTON_PINS.items():
        gpio.setup(pin, gpio.IN)
        gpio.add_event_detect(pin, gpio.FALLING, callback=callback, bouncetime=100)
        
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()