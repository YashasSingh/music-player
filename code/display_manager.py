import pygame
import os
from PIL import Image, ImageTk

class DisplayManager:
    def __init__(self):
        # Initialize pygame display
        os.environ['SDL_FBDEV'] = '/dev/fb1'  # Use SPI display
        pygame.init()
        
        # Display settings
        self.width = 480
        self.height = 320
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Turntable Player")
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.BLUE = (70, 130, 180)
        self.GREEN = (34, 139, 34)
        self.RED = (220, 20, 60)
        self.GRAY = (128, 128, 128)
        
        # Load fonts
        try:
            self.font_large = pygame.font.Font("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
            self.font_medium = pygame.font.Font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            self.font_small = pygame.font.Font("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
        except:
            # Fallback to default fonts
            self.font_large = pygame.font.Font(None, 24)
            self.font_medium = pygame.font.Font(None, 18)
            self.font_small = pygame.font.Font(None, 14)
        
        # Current display state
        self.current_track = None
        self.is_playing = False
        self.volume = 0.7
        self.speed = 1.0
        self.bluetooth_on = False
        
        print("Display manager initialized")
    
    def update_track_info(self, track_info):
        """Update displayed track information"""
        self.current_track = track_info
    
    def update_play_state(self, playing):
        """Update play/pause state"""
        self.is_playing = playing
    
    def update_controls(self, volume, speed):
        """Update volume and speed display"""
        self.volume = volume
        self.speed = speed
    
    def update_bluetooth_status(self, enabled):
        """Update bluetooth status"""
        self.bluetooth_on = enabled
    
    def draw_text_centered(self, text, font, color, y_pos):
        """Draw centered text at specified y position"""
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect(center=(self.width // 2, y_pos))
        self.screen.blit(text_surface, text_rect)
    
    def draw_progress_bar(self, x, y, width, height, progress, color):
        """Draw a progress bar"""
        # Background
        pygame.draw.rect(self.screen, self.GRAY, (x, y, width, height))
        # Progress
        progress_width = int(width * progress)
        pygame.draw.rect(self.screen, color, (x, y, progress_width, height))
        # Border
        pygame.draw.rect(self.screen, self.WHITE, (x, y, width, height), 2)
    
    def refresh(self):
        """Refresh the display with current information"""
        # Clear screen
        self.screen.fill(self.BLACK)
        
        if self.current_track:
            # Album art (if available)
            if self.current_track.get('album_art'):
                try:
                    # Convert PIL image to pygame surface
                    art_data = self.current_track['album_art']
                    pygame_image = pygame.image.fromstring(
                        art_data.tobytes(), art_data.size, art_data.mode)
                    self.screen.blit(pygame_image, (20, 20))
                except Exception as e:
                    print(f"Error displaying album art: {e}")
            
            # Track title
            title = self.current_track['title']
            if len(title) > 25:
                title = title[:22] + "..."
            self.draw_text_centered(title, self.font_large, self.WHITE, 160)
            
            # Artist
            artist = self.current_track['artist']
            if len(artist) > 30:
                artist = artist[:27] + "..."
            self.draw_text_centered(artist, self.font_medium, self.BLUE, 190)
            
            # Album
            album = self.current_track['album']
            if len(album) > 35:
                album = album[:32] + "..."
            self.draw_text_centered(album, self.font_small, self.GRAY, 210)
        
        # Play/Pause indicator
        play_text = "⏸️ PAUSED" if not self.is_playing else "▶️ PLAYING"
        play_color = self.RED if not self.is_playing else self.GREEN
        self.draw_text_centered(play_text, self.font_medium, play_color, 240)
        
        # Volume control
        vol_text = f"Volume: {int(self.volume * 100)}%"
        text_surface = self.font_small.render(vol_text, True, self.WHITE)
        self.screen.blit(text_surface, (20, 270))
        self.draw_progress_bar(120, 275, 100, 10, self.volume, self.BLUE)
        
        # Speed control
        speed_text = f"Speed: {self.speed:.1f}x"
        text_surface = self.font_small.render(speed_text, True, self.WHITE)
        self.screen.blit(text_surface, (260, 270))
        speed_progress = (self.speed - 0.5) / 1.5  # Map 0.5-2.0 to 0-1
        self.draw_progress_bar(340, 275, 100, 10, speed_progress, self.GREEN)
        
        # Bluetooth status
        bt_text = "🔵 BT ON" if self.bluetooth_on else "⚫ BT OFF"
        bt_color = self.BLUE if self.bluetooth_on else self.GRAY
        text_surface = self.font_small.render(bt_text, True, bt_color)
        self.screen.blit(text_surface, (380, 295))
        
        # Update display
        pygame.display.flip()
    
    def cleanup(self):
        """Clean up pygame resources"""
        pygame.quit()
        print("Display manager cleaned up")
