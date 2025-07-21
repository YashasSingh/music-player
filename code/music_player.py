import os
import random
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC
import io
from PIL import Image

class MusicPlayer:
    def __init__(self):
        self.playlist = []
        self.current_index = 0
        self.shuffle_mode = False
    
    def scan_library(self, music_dir):
        """Scan directory for MP3 files and extract metadata"""
        music_path = Path(music_dir)
        if not music_path.exists():
            print(f"Music directory {music_dir} not found!")
            return
        
        print("Scanning music library...")
        for mp3_file in music_path.rglob("*.mp3"):
            try:
                track_info = self.extract_metadata(mp3_file)
                if track_info:
                    self.playlist.append(track_info)
                    print(f"Added: {track_info['title']} - {track_info['artist']}")
            except Exception as e:
                print(f"Error processing {mp3_file}: {e}")
        
        print(f"Library scan complete. Found {len(self.playlist)} tracks.")
        
        # Shuffle playlist initially
        if self.playlist:
            random.shuffle(self.playlist)
    
    def extract_metadata(self, file_path):
        """Extract metadata and album art from MP3 file"""
        try:
            audio_file = MP3(file_path, ID3=ID3)
            
            # Extract basic metadata
            title = str(audio_file.get('TIT2', ['Unknown Title'])[0])
            artist = str(audio_file.get('TPE1', ['Unknown Artist'])[0])
            album = str(audio_file.get('TALB', ['Unknown Album'])[0])
            duration = int(audio_file.info.length)
            
            # Extract album art
            album_art = None
            for tag in audio_file.tags.values():
                if isinstance(tag, APIC):
                    try:
                        album_art = Image.open(io.BytesIO(tag.data))
                        # Resize to fit display
                        album_art = album_art.resize((120, 120), Image.Resampling.LANCZOS)
                        break
                    except Exception as e:
                        print(f"Error processing album art: {e}")
            
            return {
                'file_path': str(file_path),
                'title': title,
                'artist': artist,
                'album': album,
                'duration': duration,
                'album_art': album_art
            }
            
        except Exception as e:
            print(f"Error extracting metadata from {file_path}: {e}")
            return None
    
    def get_current_track(self):
        """Get currently selected track"""
        if self.playlist and 0 <= self.current_index < len(self.playlist):
            return self.playlist[self.current_index]
        return None
    
    def next_track(self):
        """Move to next track"""
        if self.playlist:
            self.current_index = (self.current_index + 1) % len(self.playlist)
            return self.get_current_track()
        return None
    
    def previous_track(self):
        """Move to previous track"""
        if self.playlist:
            self.current_index = (self.current_index - 1) % len(self.playlist)
            return self.get_current_track()
        return None
    
    def format_duration(self, seconds):
        """Format duration as MM:SS"""
        minutes = seconds // 60
        seconds = seconds % 60
        return f"{minutes:02d}:{seconds:02d}"
