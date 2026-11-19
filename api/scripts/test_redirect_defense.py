from unittest.mock import MagicMock
from fastapi import HTTPException
from app.routers.redirect import redirect_to_long_url
from app.models import Link

mock_request = MagicMock()
mock_request.client.host = "127.0.0.1"
mock_request.headers = {}

# Test 1: Active safe link redirects (307)
safe_link = Link(id=1, code="safe1", long_url="https://example.com", expires_at=None)
mock_db = MagicMock()
mock_db.query().filter().first.return_value = safe_link

resp = redirect_to_long_url("safe1", mock_request, mock_db)
assert resp.status_code == 307
assert resp.headers["location"] == "https://example.com"
print("[PASS] Safe link returned HTTP 307 to https://example.com")

# Test 2: Poisoned database row with javascript: scheme is caught by defense-in-depth (raises 404)
poisoned_link = Link(id=2, code="poisoned1", long_url="javascript:alert(1)", expires_at=None)
mock_db.query().filter().first.return_value = poisoned_link

try:
    redirect_to_long_url("poisoned1", mock_request, mock_db)
    print("[FAIL] Poisoned link was not blocked!")
    exit(1)
except HTTPException as e:
    assert e.status_code == 404
    print("[PASS] Poisoned link blocked by defense-in-depth (returned HTTP 404 Not Found)")

print("\nAll redirect defense tests passed!")
