import urllib.request
import json
import sys

# Ensure stdout/stderr handles Unicode safely on Windows
for stream in (sys.stdout, sys.stderr):
    reconfig = getattr(stream, "reconfigure", None)
    if callable(reconfig):
        try:
            reconfig(encoding="utf-8", errors="replace")
        except Exception:
            pass

FRONTEND_URL = "http://taskflow-frontend-prod-2k26.s3-website.ap-south-1.amazonaws.com"
BACKEND_URL = "http://13.234.146.200"


print("=" * 60)
print("TASKFLOW AWS PRODUCTION DEPLOYMENT VALIDATION")
print("=" * 60)

# 1. Test Frontend S3 Hosting
print("\n[1/5] Testing Frontend S3 Hosting...")
try:
    with urllib.request.urlopen(FRONTEND_URL, timeout=5) as res:
        assert res.status == 200
        html = res.read().decode('utf-8')
        assert "TaskFlow" in html or "root" in html
        print(f"  ✅ S3 Website root is serving HTML (Status {res.status})")
except Exception as e:
    print(f"  ❌ S3 Website failed: {e}")
    sys.exit(1)

# 2. Test Frontend SPA Route Redirect
print("\n[2/5] Testing Frontend SPA Client-Side Routing...")
try:
    with urllib.request.urlopen(f"{FRONTEND_URL}/login", timeout=5) as res:
        assert res.status == 200
        print(f"  ✅ S3 SPA routing for /login resolved successfully (Status {res.status})")
except Exception as e:
    print(f"  ❌ S3 SPA routing failed: {e}")
    sys.exit(1)

# 3. Test Backend Health
print("\n[3/5] Testing Backend Health Endpoint...")
try:
    with urllib.request.urlopen(f"{BACKEND_URL}/health", timeout=5) as res:
        assert res.status == 200
        body = json.loads(res.read())
        assert body.get("status") == "ok"
        print(f"  ✅ Backend health check passed: {body}")
except Exception as e:
    print(f"  ❌ Backend health check failed: {e}")
    sys.exit(1)

# 4. Test Live Authentication & JWT Generation
print("\n[4/5] Testing Authentication & JWT issuance...")
try:
    login_data = json.dumps({"email": "admin@taskflow.dev", "password": "Admin@123456"}).encode('utf-8')
    req = urllib.request.Request(
        f"{BACKEND_URL}/api/v1/auth/login",
        data=login_data,
        headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as res:
        assert res.status == 200
        tokens = json.loads(res.read())
        token = tokens["access_token"]
        assert token is not None
        print(f"  ✅ Login successful! Token type: {tokens.get('token_type', 'bearer')}")
except Exception as e:
    print(f"  ❌ Authentication test failed: {e}")
    sys.exit(1)

# 5. Test Database Query through API (RDS PostgreSQL)
print("\n[5/5] Testing RDS PostgreSQL Queries (Projects & Tasks)...")
try:
    req = urllib.request.Request(
        f"{BACKEND_URL}/api/v1/projects",
        headers={"Authorization": f"Bearer {token}"}
    )
    with urllib.request.urlopen(req, timeout=5) as res:
        assert res.status == 200
        projects = json.loads(res.read())
        assert len(projects) > 0
        print(f"  ✅ Successfully retrieved {len(projects)} seeded projects from RDS:")
        for p in projects:
            print(f"     • [{p['id']}] {p['name']} (active={p['is_active']})")
except Exception as e:
    print(f"  ❌ RDS query failed: {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL AWS SERVICES OPERATIONAL & VERIFIED!")
print("=" * 60)
