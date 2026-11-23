import json
import urllib.request
import urllib.error

base = "http://localhost:3000"

print("--- PROBE 1: POST /links ---")
req1 = urllib.request.Request(
    f"{base}/links",
    data=json.dumps({"long_url": "https://example.com/story-test"}).encode("utf-8"),
    headers={"Content-Type": "application/json", "X-Request-ID": "test-req-001"}
)
with urllib.request.urlopen(req1) as resp:
    body1 = json.loads(resp.read().decode())
    short_code = body1["code"]
    print(f"Status: {resp.status}, X-Request-ID: {resp.headers.get('X-Request-ID')}, Created: {short_code}")

print("\n--- PROBE 2: GET /r/{short_code} ---")
class NoRedirectHandler(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

opener = urllib.request.build_opener(NoRedirectHandler)
req2 = urllib.request.Request(f"{base}/r/{short_code}", headers={"X-Request-ID": "test-req-002"})
try:
    resp2 = opener.open(req2)
    print(f"Status: {resp2.status}, X-Request-ID: {resp2.headers.get('X-Request-ID')}, Location: {resp2.headers.get('Location')}")
except urllib.error.HTTPError as e:
    print(f"Status: {e.code}, X-Request-ID: {e.headers.get('X-Request-ID')}, Location: {e.headers.get('Location')}")

print("\n--- PROBE 3: GET /r/missing99 ---")
req3 = urllib.request.Request(f"{base}/r/missing99", headers={"X-Request-ID": "test-req-003"})
try:
    with urllib.request.urlopen(req3) as resp3:
        print(f"Status: {resp3.status}")
except urllib.error.HTTPError as e:
    body3 = json.loads(e.read().decode())
    print(f"Status: {e.code}, X-Request-ID: {e.headers.get('X-Request-ID')}, Body: {body3}")
