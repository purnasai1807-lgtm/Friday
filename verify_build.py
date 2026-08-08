# Quick verification script for FRIDAY build
import io
import sys

files = ['app.py', 'friday_listener.py', 'friday_listener.pyw',
         'friday_agent.py', 'friday_app.py', 'friday_core.py']
all_ok = True
for f in files:
    try:
        src = io.open(f, encoding='utf-8').read()
        compile(src, f, 'exec')
        print(f + ' OK')
    except Exception as e:
        all_ok = False
        print(f + ' FAIL: ' + str(e))

# Check script.js has no removed button refs
try:
    js = io.open('static/script.js', encoding='utf-8').read()
    bad_refs = [r for r in ['sendBtn', 'theme-thumb', 'wakeBtn', 'sleepBtn', 'listenBtn'] if r in js]
    if bad_refs:
        all_ok = False
        print('script.js still references removed UI elements: ' + str(bad_refs))
    else:
        print('script.js OK (no removed button refs)')
except Exception as e:
    all_ok = False
    print('script.js read FAIL: ' + str(e))

print('ALL_OK' if all_ok else 'HAS_ERRORS')
sys.exit(0 if all_ok else 1)

