import urllib.request
import time
import sys

url = "http://13.234.146.200/health"
print(f"Polling {url} for backend readiness...")

start_time = time.time()
max_wait = 240  # 4 minutes

while time.time() - start_time < max_wait:
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'TaskFlowHealthCheck/1.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            if response.status == 200:
                body = response.read().decode('utf-8')
                print(f"\nSUCCESS! Backend is online and healthy!")
                print(f"Response: {body}")
                sys.exit(0)
    except Exception as e:
        elapsed = int(time.time() - start_time)
        print(f"[{elapsed}s] Waiting for backend initialization... ({type(e).__name__})")
    time.sleep(10)

print("\nTimed out waiting for backend to become healthy.")
sys.exit(1)
