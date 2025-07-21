#!/usr/bin/env python3
import pygame
import threading
import time
import os
from pathlib import Path
from code.music_player import MusicPlayer
from code.hardware_interface import HardwareInterface
from code.display_manager import DisplayManager

class TurntablePlayer:
    def __init__(self):
        # Initialize pygame mixer for audio
        pygame.mixer.pre_init(frequency=44100, size=-16, channels=2, buffer=512)
        pygame.mixer.init()
        
        # Initialize components
        self.music_player = MusicPlayer()
        self.hardware = HardwareInterface()
        self.display = DisplayManager()
        
        # State variables
        self.is_playing = False
        self.current_volume = 0.7
        self.playback_speed = 1.0
        self.bluetooth_enabled = False
        
        # Set up callbacks
        self.hardware.set_button_callbacks(
            play_pause=self.toggle_play_pause,
            next_track=self.next_track,
            bluetooth=self.toggle_bluetooth
        )
        
        # Load music library
        self.music_player.scan_library("/home/pi/Music")
        
        print("Turntable Player initialized successfully!")
    
    def toggle_play_pause(self):
        """Handle play/pause button press"""
        if self.is_playing:
            pygame.mixer.music.pause()
            self.is_playing = False
            print("Paused")
        else:
            if pygame.mixer.music.get_busy():
                pygame.mixer.music.unpause()
            else:
                current_track = self.music_player.get_current_track()
                if current_track:
                    pygame.mixer.music.load(current_track['file_path'])
                    pygame.mixer.music.play()
            self.is_playing = True
            print("Playing")
        
        self.display.update_play_state(self.is_playing)
    
    def next_track(self):
        """Skip to next track"""
        next_track = self.music_player.next_track()
        if next_track:
            pygame.mixer.music.load(next_track['file_path'])
            if self.is_playing:
                pygame.mixer.music.play()
            self.display.update_track_info(next_track)
            print(f"Next track: {next_track['title']}")
    
    def toggle_bluetooth(self):
        """Toggle bluetooth connectivity"""
        self.bluetooth_enabled = not self.bluetooth_enabled
        if self.bluetooth_enabled:
            os.system("sudo systemctl start bluetooth")
            os.system("bluetoothctl power on")
            print("Bluetooth enabled")
        else:
            os.system("bluetoothctl power off")
            print("Bluetooth disabled")
        
        self.display.update_bluetooth_status(self.bluetooth_enabled)
    
    def update_controls(self):
        """Update volume and speed from potentiometers"""
        volume_raw = self.hardware.read_volume_pot()
        speed_raw = self.hardware.read_speed_pot()
        
        # Map potentiometer values (0-1023) to useful ranges
        self.current_volume = volume_raw / 1023.0
        self.playback_speed = 0.5 + (speed_raw / 1023.0) * 1.5  # 0.5x to 2.0x speed
        
        # Apply volume
        pygame.mixer.music.set_volume(self.current_volume)
        
        # Update display
        self.display.update_controls(self.current_volume, self.playback_speed)
    
    def run(self):
        """Main application loop"""
        try:
            # Display initial track
            current_track = self.music_player.get_current_track()
            if current_track:
                self.display.update_track_info(current_track)
            
            # Main loop
            while True:
                self.update_controls()
                self.hardware.update()
                self.display.refresh()
                time.sleep(0.1)  # 10Hz update rate
                
        except KeyboardInterrupt:
            print("Shutting down...")
        finally:
            pygame.mixer.quit()
            self.hardware.cleanup()
            self.display.cleanup()

if __name__ == "__main__":
    player = TurntablePlayer()
    player.run()
