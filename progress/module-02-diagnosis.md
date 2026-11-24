# Module 02 Diagnosis Notes: Reading Logs Like a Story

## Bug 3: Log Level Misconfiguration & Ghost Errors
- **Symptom:** Application logs exhibited isolated error and warning records without corresponding inbound `"request received"` or `"response sent"` records. Errors appeared out of thin air with zero correlation IDs or latency measurements.
- **Hypothesis:** The effective logging level was defaulting to `WARNING`, suppressing informational request lifecycle events even though `LOG_LEVEL=INFO` was set in `api/.env`.
  - Observation: `api/app/config.py` lacked a `log_level` field on `Settings`, and `api/app/main.py` did not initialize Python's logging or attach request middleware. Hypothesis confirmed.
- **Fix:**
  - Added `log_level: str = Field(default="INFO", validation_alias="LOG_LEVEL")` to `Settings`.
  - Attached a structured JSON logging middleware in `api/app/main.py` using `try/finally` to generate or propagate `X-Request-ID` and record start/completion events with `status` and `duration_ms`.
  - Updated `api/app/routers/redirect.py` to emit structured events stamped with `req_id`.
- **Verification Proof:** Executed `api/scripts/verify_module_02_logging.py`. Verified that every probe (`POST /links`, `GET /r/:code`, `GET /r/missing99`) emits matching `"request received"` and `"response sent"` JSON records linked by `X-Request-ID`.

---

## Bug 4: Midnight Timezone Mismatch & Vanishing Links
- **Symptom:** User reports that links created around midnight UTC intermittently returned 404 for several hours before resolving normally later in the night.
- **Hypothesis:** Timestamp comparisons in validation and redirect logic suffered from timezone mismatch (comparing naive datetimes against UTC or failing to normalize client offsets into UTC), creating an artificial multi-hour expiration dead-zone around UTC midnight.
  - Observation: In `api/app/schemas/link.py`, `validate_expires_at` evaluated `cmp_v` but returned the raw input `v`, preserving client local offsets rather than storing normalized UTC datetimes in PostgreSQL `TIMESTAMPTZ`. In `api/app/routers/redirect.py`, expiration check required defensive `.astimezone(timezone.utc)`. Hypothesis confirmed.
- **Fix:**
  - Hardened `LinkCreate.validate_expires_at` to normalize any offset-aware datetime directly into `v.astimezone(timezone.utc)` and attach UTC awareness to naive datetimes, returning the normalized UTC datetime object.
  - Hardened `redirect.py` to enforce aware-to-aware UTC comparisons (`link.expires_at.astimezone(timezone.utc) <= now`).
- **Verification Proof:** Executed `api/scripts/verify_module_02_timezone.py`. Proved that links created with offsets resolve immediately (HTTP 307) and expired links fail validation with clear 400 Bad Request error.
