#!/bin/bash

# Install Python dependencies
pip3 install -r pip-requirements.txt

# Make the daemon script executable
chmod +x expanse_daemon.py

# Create symlink to the daemon script
sudo ln -sf "$(pwd)/expanse_daemon.py" /usr/local/bin/expanse_daemon.py

# Copy the launchd plist to the correct location
cp com.expanse.daemon.plist ~/Library/LaunchAgents/

# Load the daemon
launchctl load ~/Library/LaunchAgents/com.expanse.daemon.plist

echo "Expanse daemon installed successfully!"
echo "You can now use Ctrl+Alt+E to trigger the expansion menu."
echo "To manage your expansions, run: python3 expanse_daemon.py" 