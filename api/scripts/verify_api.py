import sys
import time
import subprocess
import os
import json
import re

api_dir = r"d:\knacklab\api"
env = os.environ.copy()
env["PYTHONPATH"] = api_dir

evidence_path = r"d:\knacklab\progress\evidence\module-03\api-evidence.txt"
lines = []

print("Starting Uvicorn server on 127.0.0.1:8000...", flush=True)
proc = subprocess.Popen(
    [os.path.join(api_dir, ".venv", "Scripts", "uvicorn.exe"), "app.main:app", "--port", "8000", "--host", "127.0.0.1"],
    cwd=api_dir,
    env=env,
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL
)

def run_curl(args):
    res = subprocess.run(["curl.exe", "-s", "-i"] + args, capture_output=True, text=True, timeout=5)
    return res.stdout

try:
    # Wait for server to be responsive
    for attempt in range(10):
        time.sleep(1)
        try:
            test_resp = run_curl(["http://localhost:8000/health"])
            if "200 OK" in test_resp:
                print(f"Uvicorn is ready after {attempt + 1}s!", flush=True)
                break
        except Exception:
            pass
    else:
        raise RuntimeError("Uvicorn failed to start within 10 seconds")

    # 1. Health check
    out1 = run_curl(["http://localhost:8000/health"])
    lines.append("=== 1. HEALTH CHECK: GET /health ===")
    lines.append(out1.strip())
    print("Health check completed", flush=True)

    # 2. Valid link create
    out2 = run_curl(["-X", "POST", "http://localhost:8000/links", "-H", "Content-Type: application/json", "-d", '{"long_url":"https://example.com"}'])
    lines.append("=== 2. CREATE LINK: POST /links with https://example.com ===")
    lines.append(out2.strip())
    print("Create link completed", flush=True)

    # Extract code
    m = re.search(r'"code":"([^"]+)"', out2)
    code = m.group(1) if m else None
    id_m = re.search(r'"id":([0-9]+)', out2)
    link_id = id_m.group(1) if id_m else None

    if code:
        # 3. Redirect
        out3 = run_curl([f"http://localhost:8000/r/{code}"])
        lines.append(f"=== 3. REDIRECT: GET /r/{code} ===")
        lines.append(out3.strip())
        print(f"Redirect GET /r/{code} completed", flush=True)

        # 4. Get link by id
        if link_id:
            out4 = run_curl([f"http://localhost:8000/links/{link_id}"])
            lines.append(f"=== 4. GET LINK BY ID: GET /links/{link_id} ===")
            lines.append(out4.strip())
            print(f"Get link /links/{link_id} completed", flush=True)

    # 5. Non-existent link
    out5 = run_curl(["http://localhost:8000/r/nonexistent404code"])
    lines.append("=== 5. NON-EXISTENT LINK: GET /r/nonexistent404code ===")
    lines.append(out5.strip())
    print("404 check completed", flush=True)

    # 6. Abuse cases
    abuse_cases = [
        "javascript:alert(1)",
        "JaVaScRiPt:alert(1)",
        " javascript:alert(1) ",
        "data:text/html,<svg/onload=alert(1)>",
        "//evil.example.com",
        "http:%2f%2fevil.example.com",
        "http%3A%2F%2Fevil.example.com",
        "http:\\evil.example.com",
        "https://good.com@evil.example.com"
    ]

    for tc in abuse_cases:
        payload = json.dumps({"long_url": tc})
        out_abuse = run_curl(["-X", "POST", "http://localhost:8000/links", "-H", "Content-Type: application/json", "-d", payload])
        status = out_abuse.splitlines()[0] if out_abuse.splitlines() else "NO RESPONSE"
        lines.append(f"=== ABUSE CHECK ({status}): {tc} ===")
        lines.append(out_abuse.strip())
        print(f"Abuse check: {tc} -> {status}", flush=True)

    with open(evidence_path, "w", encoding="utf-8") as f:
        f.write("\n\n".join(lines))
    print(f"Evidence successfully written to {evidence_path}", flush=True)

finally:
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()
    print("Uvicorn server stopped.", flush=True)
