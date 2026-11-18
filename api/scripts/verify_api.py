import sys
import time
import subprocess
import os

python_exe = sys.executable
api_dir = r"d:\knacklab\api"
env = os.environ.copy()
env["PYTHONPATH"] = api_dir

# Start uvicorn
proc = subprocess.Popen(
    [os.path.join(api_dir, ".venv", "Scripts", "uvicorn.exe"), "app.main:app", "--port", "8000", "--host", "127.0.0.1"],
    cwd=api_dir,
    env=env,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE
)

evidence_path = r"d:\knacklab\progress\evidence\module-03\api-evidence.txt"
lines = []

def run_curl(args):
    res = subprocess.run(["curl.exe", "-s", "-i"] + args, capture_output=True, text=True)
    return res.stdout

try:
    time.sleep(3)
    
    # 1. Health check
    out1 = run_curl(["http://localhost:8000/health"])
    lines.append("=== 1. HEALTH CHECK: GET /health ===")
    lines.append(out1)
    print("Health check completed")

    # 2. Valid link create
    out2 = run_curl(["-X", "POST", "http://localhost:8000/links", "-H", "Content-Type: application/json", "-d", '{"long_url":"https://example.com"}'])
    lines.append("=== 2. CREATE LINK: POST /links with https://example.com ===")
    lines.append(out2)
    print("Create link completed")

    # Extract code
    import re
    m = re.search(r'"code":"([^"]+)"', out2)
    code = m.group(1) if m else None
    id_m = re.search(r'"id":([0-9]+)', out2)
    link_id = id_m.group(1) if id_m else None

    if code:
        # 3. Redirect
        out3 = run_curl([f"http://localhost:8000/r/{code}"])
        lines.append(f"=== 3. REDIRECT: GET /r/{code} ===")
        lines.append(out3)
        print("Redirect completed")

        # 4. Get link by id
        out4 = run_curl([f"http://localhost:8000/links/{link_id}"])
        lines.append(f"=== 4. GET LINK BY ID: GET /links/{link_id} ===")
        lines.append(out4)
        print("Get link completed")

    # 5. Non-existent link
    out5 = run_curl(["http://localhost:8000/r/nonexistent404code"])
    lines.append("=== 5. NON-EXISTENT LINK: GET /r/nonexistent404code ===")
    lines.append(out5)
    print("404 check completed")

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

    import json
    for tc in abuse_cases:
        payload = json.dumps({"long_url": tc})
        out_abuse = run_curl(["-X", "POST", "http://localhost:8000/links", "-H", "Content-Type: application/json", "-d", payload])
        status = out_abuse.splitlines()[0] if out_abuse.splitlines() else "NO RESPONSE"
        lines.append(f"=== ABUSE CHECK ({status}): {tc} ===")
        lines.append(out_abuse)
        print(f"Abuse check: {tc} -> {status}")

    with open(evidence_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))
    print(f"Evidence written to {evidence_path}")

finally:
    proc.terminate()
    try:
        proc.wait(timeout=3)
    except Exception:
        proc.kill()
