"""
FRIDAY AI - Network Status Checker
Shows the current status and network access URL.
"""
import socket
import urllib.request
import json
import sys

def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "localhost"

def check_server():
    try:
        resp = urllib.request.urlopen('http://127.0.0.1:5000/api/status', timeout=2)
        data = json.loads(resp.read())
        return data
    except Exception:
        return None

def main():
    ip = get_local_ip()
    status = check_server()

    print("=" * 50)
    print("FRIDAY AI - Network Status")
    print("=" * 50)

    if status:
        print(f"\nStatus: ONLINE")
        print(f"Name: {status.get('name', 'FRIDAY')}")
        print(f"Awake: {status.get('awake', False)}")
        print(f"AI Mode: {'ON' if status.get('llm_available') else 'OFF'}")
        print(f"\nAccess URLs:")
        print(f"  This PC:  http://127.0.0.1:5000")
        print(f"  Network:  http://{ip}:5000")
        print(f"\nLearning Stats:")
        stats = status.get('learning_stats', {})
        if stats:
            print(f"  Routines: {stats.get('routines_learned', 0)}")
            print(f"  Preferences: {stats.get('preferences_learned', 0)}")
            print(f"  Knowledge: {stats.get('knowledge_nodes', 0)}")
            print(f"  Success Rate: {stats.get('success_rate', 0):.0%}")
    else:
        print(f"\nStatus: OFFLINE")
        print(f"\nFRIDAY server is not running.")
        print(f"Start it with: python app.py")
        print(f"\nOnce running, access at:")
        print(f"  http://{ip}:5000")

    print("\n" + "=" * 50)
    input("Press Enter to exit...")

if __name__ == '__main__':
    main()
