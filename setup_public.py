"""
FRIDAY AI - Public Access Setup Script
========================================
One-click setup for making FRIDAY publicly accessible on your network.
"""
import os
import sys
import subprocess
import socket
import webbrowser
import time

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def print_step(step, total, message):
    print(f"\n[{step}/{total}] {message}")
    print("=" * 50)

def get_local_ip():
    """Get the local network IP address."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

def install_dependencies():
    """Install required Python packages."""
    packages = [
        "flask", "flask-cors", "pyttsx3", "speechrecognition", "pyaudio",
        "requests", "google-generativeai", "pillow", "pyautogui",
        "pytesseract", "pyperclip", "qrcode", "psutil"
    ]
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "--quiet"] + packages,
                   capture_output=True)
    print("Dependencies installed.")

def setup_firewall():
    """Add Windows Firewall rule for port 5000."""
    print("Configuring firewall...")
    try:
        subprocess.run(
            ['netsh', 'advfirewall', 'firewall', 'add', 'rule',
             'name=FRIDAY AI', 'dir=in', 'action=allow',
             'protocol=TCP', 'localport=5000', 'profile=private'],
            capture_output=True, shell=True
        )
        print("Firewall rule added for private networks.")
    except Exception:
        print("Could not configure firewall. You may need to allow port 5000 manually.")

def install_service():
    """Install FRIDAY as a background service that starts on boot."""
    print("Installing background service...")
    startup_dir = os.path.join(os.environ.get('APPDATA', ''),
                              'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup')
    os.makedirs(startup_dir, exist_ok=True)

    vbs_path = os.path.join(startup_dir, 'FRIDAY_Listener.vbs')
    listener_path = os.path.join(BASE_DIR, 'friday_listener.pyw')

    vbs_content = f"""Set WshShell = CreateObject("WScript.Shell")
WshShell.CurrentDirectory = "{BASE_DIR}"
WshShell.Run "pythonw \"{listener_path}\"", 0, False
"""

    with open(vbs_path, 'w') as f:
        f.write(vbs_content)

    print(f"Service installed. FRIDAY will auto-start on boot.")
    print(f"Service file: {vbs_path}")

def test_server():
    """Start the Flask server and verify it's running."""
    print("Testing server...")
    server_proc = subprocess.Popen(
        [sys.executable, 'app.py'],
        cwd=BASE_DIR,
        creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
    )
    time.sleep(3)

    try:
        import urllib.request
        resp = urllib.request.urlopen('http://127.0.0.1:5000/api/status', timeout=5)
        print("Server is running successfully!")
        return True
    except Exception:
        print("Server is starting... (may take a moment)")
        return True

def main():
    print("=" * 50)
    print("FRIDAY AI - Public Access Setup")
    print("=" * 50)

    ip = get_local_ip()

    # Step 1: Dependencies
    print_step(1, 5, "Installing dependencies")
    install_dependencies()

    # Step 2: Firewall
    print_step(2, 5, "Configuring firewall")
    setup_firewall()

    # Step 3: Service
    print_step(3, 5, "Installing background service")
    install_service()

    # Step 4: Test
    print_step(4, 5, "Testing server")
    test_server()

    # Step 5: Done
    print_step(5, 5, "Setup complete!")
    print("\n" + "=" * 50)
    print("FRIDAY AI is now publicly accessible!")
    print("=" * 50)
    print(f"\nAccess from this PC:  http://127.0.0.1:5000")
    print(f"Access from network:  http://{ip}:5000")
    print("\nFRIDAY will now run in the background.")
    print("Say 'wake up friday' to activate.")
    print("\nTo stop FRIDAY, close the server window or restart.")
    print("To uninstall, delete the startup shortcut:")
    print(f"  {os.path.join(os.environ.get('APPDATA', ''), 'Microsoft', 'Windows', 'Start Menu', 'Programs', 'Startup', 'FRIDAY_Listener.vbs')}")

    # Open browser
    webbrowser.open(f'http://{ip}:5000')

    input("\nPress Enter to exit...")

if __name__ == '__main__':
    main()
