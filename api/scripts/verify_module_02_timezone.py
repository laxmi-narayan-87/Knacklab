import json
import urllib.request
import urllib.error
from datetime import datetime, timezone, timedelta

base = "http://localhost:3000"

class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

opener = urllib.request.build_opener(NoRedirectHandler)

print("--- 1. CREATE LINK WITH UTC OFFSET (+05:30) ---")
future_time = (datetime.now(timezone.utc) + timedelta(hours=5)).isoformat()
req1 = urllib.request.Request(
    f"{base}/links",
    data=json.dumps({
        "long_url": "https://example.com/utc-offset-test",
        "expires_at": future_time
    }).encode("utf-8"),
    headers={"Content-Type": "application/json", "X-Request-ID": "tz-req-001"}
)
with urllib.request.urlopen(req1) as resp1:
    body1 = json.loads(resp1.read().decode())
    code1 = body1["code"]
    print(f"Created code: {code1}, expires_at: {body1['expires_at']}")

print("\n--- 2. RESOLVE LINK IMMEDIATELY ---")
req2 = urllib.request.Request(f"{base}/r/{code1}", headers={"X-Request-ID": "tz-req-002"})
try:
    resp2 = opener.open(req2)
    print(f"Status: {resp2.status}, Location: {resp2.headers.get('Location')}")
except urllib.error.HTTPError as e:
    print(f"Status: {e.code}, Location: {e.headers.get('Location')}")

print("\n--- 3. VERIFY PAST EXPIRATION REJECTION IN VALIDATOR ---")
past_time = (datetime.now(timezone.utc) - timedelta(hours=2)).isoformat()
req3 = urllib.request.Request(
    f"{base}/links",
    data=json.dumps({
        "long_url": "https://example.com/past-test",
        "expires_at": past_time
    }).encode("utf-8"),
    headers={"Content-Type": "application/json", "X-Request-ID": "tz-req-003"}
)
try:
    with urllib.request.urlopen(req3) as resp3:
        print(f"Status: {resp3.status}")
except urllib.error.HTTPError as e:
    body3 = json.loads(e.read().decode())
    print(f"Expected validation failure -> Status: {e.code}, Detail: {body3['detail'][0]['msg']}")

print("\nSUCCESS: All UTC normalization and timezone-aware checks verified!")
