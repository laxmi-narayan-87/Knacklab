# Knacklab — Engineering Portfolio & Production Labs

A collection of production-grade engineering implementations, systems architecture labs, and AI-augmented software engineering practices developed through the **Upsk Engineering Bootcamp** by **Laxmi Narayan** ([@laxmi-narayan-87](https://www.upsk.to/laxmi-narayan-87)).

---

## 🏆 Current Progress & Achievements

### 1. System Design Fundamentals (`Launchpad` Pack) — **COMPLETED (30/30)**
* **Scenario:** Public Consumer URL Shortener & Analytics Service (`public_consumer`)
* **Pack Final Score:** `30 / 30 (100% Strong)` across all 5 evaluation dimensions:
  * `tradeoff_reasoning` (5.0 / 5.0)
  * `debugging_methodology` (5.0 / 5.0)
  * `security_awareness` (5.0 / 5.0)
  * `production_thinking` (5.0 / 5.0)
  * `communication_clarity` (5.0 / 5.0)

| Module | Architecture & Deliverables | Verification Status | Score |
| :--- | :--- | :---: | :---: |
| **Module 01: Setup & Clean Code** | Single-app repo architecture (`api/`), centralized Pydantic configuration (`config.py`), `.env` fail-fast validation, container lifecycle resilience. | `GET /health` &rarr; `200 OK` | **10 / 10** |
| **Module 02: Database Design & Selection** | PostgreSQL database with SQLAlchemy 2.0 + Alembic, relational `links` and append-only `click_events`, composite B-tree indexing `(link_id, clicked_at)`. | Seed & retrieval query verified | **10 / 10** |
| **Module 03: Core API, CRUD & Safe Redirects** | Prefix routing `/r/{code}`, strict Pydantic URL scheme allowlisting (`http`/`https`), stored XSS defense, defense-in-depth redirect handler, SHA-256 IP pseudonymization. | 9 attack vectors rejected (`400`), safe `307` redirect, `404` error handling | **10 / 10** |

---

### 2. AI-Augmented Engineering (`Launchpad` Pack) — **IN PROGRESS**
* **Scenario:** Team Collaboration API (`team-collaboration`)

| Module | Core Competencies | Verification Status | Score |
| :--- | :--- | :---: | :---: |
| **Module 01: Mindset & First AI Collaboration** | "Capable Intern" mental model, responsibility boundary, Task-by-Task delegation, constraint-driven prompts, trust-audit verification, disproving overconfident hallucinations. | Architecture summary & trust audit documented; test suite verified | **10 / 10** |
| **Module 02: Task Decomposition & Interface Contracts** | The 60/40 rule, atomic task principle, interface contracts, acceptance test specifications. | *In Progress* | — |

---

## 📂 Repository Structure

```text
knacklab/
├── api/                             # FastAPI Backend (System Design Fundamentals)
│   ├── app/
│   │   ├── routers/
│   │   │   ├── links.py             # CRUD endpoints: POST /links, GET /links, GET /links/{id}
│   │   │   └── redirect.py          # Public redirect: GET /r/{code} with defense-in-depth & audit logging
│   │   ├── schemas/
│   │   │   └── link.py              # Strict Pydantic v2 URL validation schemas
│   │   ├── config.py                # Fail-fast settings management
│   │   ├── db.py                    # SQLAlchemy engine & session dependency
│   │   ├── main.py                  # FastAPI app & custom 400 validation exception handler
│   │   └── models.py                # Link and ClickEvent database models
│   ├── alembic/                     # Database migrations
│   ├── scripts/                     # Automated test and verification scripts
│   │   ├── test_validation_regression.py  # 12-vector URL validation regression suite
│   │   ├── test_redirect_defense.py       # Egress redirect defense-in-depth verification
│   │   ├── verify_api.py                  # End-to-end API test runner
│   │   └── verify-module-03.ps1           # PowerShell smoke-test drill
│   └── requirements.txt
│
├── src/                             # Node.js Service (AI-Augmented Engineering)
│   ├── models/store.js              # In-memory domain store (users, teams, invitations)
│   ├── routes/index.js              # Declarative route registry
│   └── services/workspace.js        # Domain workspace service
│
├── tests/
│   └── starter.test.js              # Native Node.js test runner suite (node --test)
│
├── progress/                        # Learning Ledger, Evaluations & Evidence
│   ├── state.json                   # Cumulative bootcamp state machine
│   ├── eval_module_01.json          # System Design Module 01 Evaluation (10/10)
│   ├── eval_module_02.json          # System Design Module 02 Evaluation (10/10)
│   ├── eval_module_03.json          # System Design Module 03 Evaluation (10/10)
│   ├── eval_ai_module_01.json       # AI-Augmented Engineering Module 01 Evaluation (10/10)
│   ├── architecture-summary.md      # Grounded workspace architecture extraction
│   ├── trust-audit.md               # Empirical verification and hallucination audit log
│   └── evidence/                    # Captured execution traces and test logs
│
├── package.json                     # Node.js project configuration
└── README.md
```

---

## 🚀 Running Verification & Tests

### Python / FastAPI Test Suite
Ensure the virtual environment is initialized (`api/.venv`):
```powershell
# Run URL validation regression test (12 attack cases)
$env:PYTHONPATH="api"; api\.venv\Scripts\python api\scripts\test_validation_regression.py

# Run redirect defense-in-depth test
$env:PYTHONPATH="api"; api\.venv\Scripts\python api\scripts\test_redirect_defense.py
```

### Node.js Test Suite
```powershell
node --test tests/starter.test.js
```

---

## 🔒 Security Principles Enforced
1. **Perimeter Validation:** All URLs must strictly use `http://` or `https://` schemes. Userinfo (`@`), backslashes (`\`), control characters, and malformed hostnames are rejected at the Pydantic schema layer with `400 Bad Request`.
2. **Defense-in-Depth:** Destination URLs are re-checked at the redirect egress boundary; poisoned database rows return `404 Not Found` rather than redirecting to unsafe destinations.
3. **Namespace Isolation:** Public redirects live under `/r/{code}`, preventing user-generated short codes from colliding with internal administrative or health endpoints.
4. **Privacy Protection:** Client IP addresses are pseudonymized using SHA-256 before recording append-only `ClickEvent` telemetry.
