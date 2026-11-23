import threading
import time
import json
import urllib.request

base = "http://localhost:3000"

def post_link(url_str):
    data = json.dumps({"long_url": url_str}).encode("utf-8")
    req = urllib.request.Request(f"{base}/links", data=data, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=3) as resp:
        return json.loads(resp.read().decode())

def get_page(p):
    req = urllib.request.Request(f"{base}/links?page={p}&limit=10")
    with urllib.request.urlopen(req, timeout=3) as resp:
        return json.loads(resp.read().decode())

def insert_worker():
    for i in range(10):
        time.sleep(0.04)
        try:
            post_link(f"https://concurrent.test/{i}")
        except Exception as e:
            print("Insert error:", e)

t = threading.Thread(target=insert_worker)
t.start()

all_ids = []
pages = {}
for p in [1, 2, 3]:
    time.sleep(0.07)
    res = get_page(p)
    ids = [item["id"] for item in res]
    pages[p] = ids
    all_ids.extend(ids)

t.join()

for p, ids in pages.items():
    print(f"Page {p} (count {len(ids)}): {ids}")

duplicates = [x for x in all_ids if all_ids.count(x) > 1]
print(f"Total fetched items: {len(all_ids)}")
print(f"Duplicates detected across pages: {set(duplicates)}")
if not duplicates:
    print("SUCCESS: 0 duplicates across pages under concurrent write traffic!")
