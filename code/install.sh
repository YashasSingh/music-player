#!/bin/bash

echo "Installing Turntable Player software..."

# Update system
sudo apt update

# Install system dependencies
sudo apt install -y python3-pip python3-pygame python3-pil python3-spidev

# Install Python packages
pip3 install -r requirements.txt

# Create music directory
mkdir -p /home/pi/Music

# Make main script executable
chmod +x turntable_player.py

# Create systemd service for auto-start
sudo tee /etc/systemd/system/turntable-player.service > /dev/null <<EOF
[Unit]
Description=Turntable Player
After=network.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/turntable
ExecStart=/usr/bin/python3 /home/pi/turntable/turntable_player.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable SPI
sudo raspi-config nonint do_spi 0

echo "Installation complete!"
echo "Copy your MP3 files to /home/pi/Music/"
echo "Run: sudo systemctl enable turntable-player.service to auto-start on boot"
echo "Run: python3 turntable_player.py to start manually"
