import os
import sys

# Ensure api directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.db import SessionLocal
from app.models import Link

def main():
    db = SessionLocal()
    test_code = "sdf-launchpad-02"
    test_long_url = "https://www.upsk.to/laxmi-narayan-87"

    try:
        # Clean up any existing record for reproducibility
        existing = db.query(Link).filter(Link.code == test_code).first()
        if existing:
            db.delete(existing)
            db.commit()

        # Insert link
        link = Link(
            code=test_code,
            long_url=test_long_url,
            created_by="student_admin"
        )
        db.add(link)
        db.commit()
        db.refresh(link)
        print(f"Inserted code: {link.code}")

        # Query by code (the core redirect path query)
        queried = db.query(Link).filter(Link.code == test_code).first()
        if not queried:
            raise RuntimeError(f"Failed to find link for code: {test_code}")

        print(f"Selected code: {queried.code}")
        print(f"Matched long_url: {queried.long_url}")

    finally:
        db.close()

if __name__ == "__main__":
    main()
