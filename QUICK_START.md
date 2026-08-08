# FRIDAY AI - Quick Start

## For Users (No Coding Required)

### 1. Install Python
Download and install Python from [python.org](https://python.org)
- Check "Add Python to PATH" during installation

### 2. Run FRIDAY
Double-click `launch_friday.bat` and choose option [1] for web server.

### 3. Access FRIDAY
Open any browser and go to:
```
http://localhost:5000
```

### 4. Voice Control
1. Allow microphone access when prompted
2. Say **"wake up friday"**
3. Give commands by voice
4. Say **"go to sleep friday"** to deactivate

## For Network/Public Access

### One-Time Setup
Double-click `PUBLIC_SETUP.bat` and follow the prompts.

### Access from Other Devices
Once setup is complete, any device on the same Wi-Fi can access:
```
http://YOUR_COMPUTER_IP:5000
```

### Auto-Start on Boot
Run `install_autostart.bat` once. FRIDAY will start automatically when Windows boots.

## Voice Commands Examples

- "What time is it?"
- "Open YouTube"
- "Search for AI news"
- "Click at 100, 200"
- "Type hello world"
- "Read the screen"
- "Take a screenshot"
- "Install Firefox"
- "Remember that my favorite color is blue"
- "Mission: build a portfolio website"
- "Tell me a joke"

## Troubleshooting

**Port 5000 already in use?**
```bash
netstat -ano | findstr :5000
taskkill /PID <PID> /F
```

**Microphone not working?**
- Use Chrome or Edge browser
- Allow microphone permission
- Check that no other app is using the microphone

**Can't access from phone?**
- Ensure both devices are on same Wi-Fi
- Check Windows Firewall allows port 5000
- Try disabling firewall temporarily to test

**Dependencies missing?**
```bash
pip install -r requirements.txt
```

## Stop FRIDAY
- Close the server window, or
- Open Task Manager and end Python processes

## Uninstall
1. Delete startup shortcut: `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\FRIDAY_Listener.vbs`
2. Delete firewall rule: `netsh advfirewall firewall delete rule name="FRIDAY AI"`
3. Delete the FRIDAY folder
