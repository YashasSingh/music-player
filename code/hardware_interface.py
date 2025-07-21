import RPi.GPIO as GPIO
import spidev
import time

class HardwareInterface:
    def __init__(self):
        # GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Button pins (adjust to match your wiring)
        self.BUTTON_PLAY = 5
        self.BUTTON_NEXT = 6 
        self.BUTTON_BT = 13
        
        # Setup buttons with pull-up resistors
        GPIO.setup(self.BUTTON_PLAY, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.BUTTON_NEXT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.BUTTON_BT, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        
        # Button state tracking for debouncing
        self.button_states = {
            self.BUTTON_PLAY: True,
            self.BUTTON_NEXT: True,
            self.BUTTON_BT: True
        }
        
        # SPI setup for ADC (MCP3008 for potentiometers)
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)  # Bus 0, Device 0
        self.spi.max_speed_hz = 1000000
        
        # Callback functions
        self.callbacks = {}
        
        print("Hardware interface initialized")
    
    def set_button_callbacks(self, play_pause=None, next_track=None, bluetooth=None):
        """Set callback functions for button presses"""
        self.callbacks = {
            self.BUTTON_PLAY: play_pause,
            self.BUTTON_NEXT: next_track,
            self.BUTTON_BT: bluetooth
        }
    
    def read_adc(self, channel):
        """Read ADC channel (0-7) using MCP3008"""
        if channel < 0 or channel > 7:
            return 0
        
        # Send command to MCP3008
        adc_command = [1, (8 + channel) << 4, 0]
        adc_response = self.spi.xfer2(adc_command)
        
        # Convert response to 10-bit value
        adc_value = ((adc_response[1] & 3) << 8) + adc_response[2]
        return adc_value
    
    def read_volume_pot(self):
        """Read volume potentiometer (ADC channel 0)"""
        return self.read_adc(0)
    
    def read_speed_pot(self):
        """Read speed potentiometer (ADC channel 1)"""
        return self.read_adc(1)
    
    def update(self):
        """Update button states and handle presses"""
        for pin, callback in self.callbacks.items():
            if callback:
                current_state = GPIO.input(pin)
                
                # Detect button press (falling edge with debouncing)
                if self.button_states[pin] and not current_state:
                    time.sleep(0.05)  # Debounce delay
                    if not GPIO.input(pin):  # Confirm button still pressed
                        callback()
                
                self.button_states[pin] = current_state
    
    def cleanup(self):
        """Clean up GPIO and SPI resources"""
        GPIO.cleanup()
        self.spi.close()
        print("Hardware interface cleaned up")
