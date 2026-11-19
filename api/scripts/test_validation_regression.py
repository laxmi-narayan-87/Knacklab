from app.schemas.link import LinkCreate
from pydantic import ValidationError

test_cases = [
    ("javascript:alert(1)", False),
    ("JaVaScRiPt:alert(1)", False),
    (" javascript:alert(1) ", False),
    ("data:text/html,<svg/onload=alert(1)>", False),
    ("//evil.example.com", False),
    ("http:%2f%2fevil.example.com", False),
    ("http%3A%2F%2Fevil.example.com", False),
    ("http:\\evil.example.com", False),
    ("https://good.com@evil.example.com", False),
    ("https://example.com\n", False),
    ("https://example.com", True),
    ("http://foo.bar/baz?q=1", True)
]

passed = 0
failed = 0

for url, expected in test_cases:
    try:
        LinkCreate(long_url=url)
        res = True
    except ValidationError:
        res = False
    
    if res == expected:
        passed += 1
        verdict = "ACCEPTED (Expected)" if res else "REJECTED (Expected)"
        print(f"[PASS] {repr(url)} -> {verdict}")
    else:
        failed += 1
        verdict = "UNEXPECTED ACCEPT" if res else "UNEXPECTED REJECT"
        print(f"[FAIL] {repr(url)} -> {verdict}")

print(f"\nResults: {passed} passed, {failed} failed.")
if failed > 0:
    exit(1)
