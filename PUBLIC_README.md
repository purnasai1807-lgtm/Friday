# FRIDAY AI - Public Deployment Guide

FRIDAY is now set up for public/network access. Anyone on your network can use it.

## Quick Start

### Option 1: One-Click Setup (Recommended)
Double-click `PUBLIC_SETUP.bat` and follow the prompts.

### Option 2: Manual Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Start the server:
   ```bash
   python app.py
   ```

3. Access from any device on the same network:
   ```
   http://YOUR_IP:5000
   ```

## Access Methods

### From this computer
```
http://127.0.0.1:5000
```

### From other devices (phone, laptop, tablet)
1. Find your computer's IP address:
   ```bash
   ipconfig
   ```
   Look for "IPv4 Address" (e.g., 192.168.1.100)

2. On any device on the same Wi-Fi/network, open:
   ```
   http://192.168.1.100:5000
   ```

### From the internet (advanced)
To access from outside your home/office network:
1. Set up port forwarding on your router (forward port 5000 to your PC's IP)
2. Use your public IP address (search "what is my IP" on Google)
3. Note: This requires configuring your router and may have security implications

## Background Operation

### Auto-start on boot
Run `install_autostart.bat` once. FRIDAY will:
- Start automatically when Windows boots
- Run in the background (no window)
- Always listen for "friday"

### Manual background mode
Run `start_friday_listener.bat` to start the always-on listener.

## Voice Control

1. Open the web app on any device
2. Allow microphone access when prompted
3. Say **"wake up friday"** to activate
4. Give commands by voice
5. Say **"go to sleep friday"** to deactivate

No buttons, no chat box - pure voice control.

## Features

- **Voice Commands**: Open apps, search web, control computer, fill forms
- **Screen Reading**: Read any text on screen, analyze errors, review code
- **Self-Learning**: Learns your routines, preferences, and predicts needs
- **Computer Control**: Click, type, drag, install software, navigate apps
- **Autonomous Tasks**: Run missions, build projects, automate workflows
- **Multi-Agent**: Planner, coder, researcher, reviewer agents work together

## Troubleshooting

### Can't access from phone?
1. Ensure both devices are on the same Wi-Fi network
2. Check Windows Firewall allows port 5000
3. Try disabling firewall temporarily to test

### Microphone not working?
1. Allow microphone access in the browser
2. Check that no other app is using the microphone
3. Try Chrome or Edge browser for best compatibility

### Server won't start?
1. Check that port 5000 is not in use
2. Ensure Python is installed and in PATH
3. Run `python app.py` manually to see error messages

## Security Notes

- FRIDAY runs on your local network by default
- The permission system requires confirmation for sensitive actions
- Keep your firewall enabled
- Don't expose port 5000 to the internet without understanding the risks
- The voice interface uses browser-based speech recognition (Google/Web Speech API)

## Stopping FRIDAY

- Close the server window, or
- Run `taskkill /F /IM python.exe` in Command Prompt, or
- Restart your computer

## Uninstall

1. Delete the startup shortcut:
   ```
   %APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\FRIDAY_Listener.vbs
   ```

2. Remove the firewall rule (optional):
   ```bash
   netsh advfirewall firewall delete rule name="FRIDAY AI"
   ```

3. Delete the FRIDAY folder

## Files

- `app.py` - Main Flask web server
- `friday_cortex.py` - Central brain/orchestrator
- `friday_control.py` - Computer control agent
- `friday_learning.py` - Self-learning memory
- `friday_vision.py` - Vision/screen reading
- `friday_listener.py` - Background voice listener
- `PUBLIC_SETUP.bat` - One-click public setup
- `install_autostart.bat` - Install auto-start service
- `start_friday.bat` - Start web server
- `start_friday_desktop.bat` - Start desktop app
- `start_friday_listener.bat` - Start background listener
