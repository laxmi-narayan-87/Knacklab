# Knacklab — Engineering Portfolio & Production Labs

A collection of production-grade engineering implementations, systems architecture labs, AI-augmented engineering practices, and production incident debugging developed through the **Upsk Engineering Bootcamp** by **Laxmi Narayan** ([@laxmi-narayan-87](https://www.upsk.to/laxmi-narayan-87)).

---

## 🏆 Current Progress & Achievements

### 1. System Design Fundamentals (`Launchpad` Pack) — **COMPLETED (30/30)**
* **Scenario:** Public Consumer URL Shortener & Analytics Service (`public_consumer`)
* **Pack Final Score:** `30 / 30 (100% Strong)` across all 5 core dimensions:
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

### 2. AI-Augmented Engineering (`Launchpad` Pack) — **COMPLETED (30/30)**
* **Scenario:** Team Collaboration API (`team-collaboration`)
* **Pack Final Score:** `30 / 30 (100% Strong)` across all 5 core dimensions:
  * `prompt_quality` (5.0 / 5.0)
  * `review_thoroughness` (5.0 / 5.0)
  * `iteration_efficiency` (5.0 / 5.0)
  * `engineering_judgment` (5.0 / 5.0)
  * `final_quality` (5.0 / 5.0)

| Module | Core Competencies & Deliverables | Verification Status | Score |
| :--- | :--- | :---: | :---: |
| **Module 01: Mindset & First AI Collaboration** | "Capable Intern" mental model, responsibility boundary, Task-by-Task delegation, constraint-driven prompts, trust-audit verification, disproving overconfident hallucinations. | Architecture summary & trust audit documented; starter tests verified | **10 / 10** |
| **Module 02: Task Decomposition & Interface Contracts** | The 60/40 rule, atomic task principle ($< 150$ LOC per task), 9-task dependency tree, bidirectional interface contracting, membership models, deterministic acceptance criteria. | 9-task dependency graph & prompt contracts documented in `progress/task-tree.md` | **10 / 10** |
| **Module 03: Context Engineering** | Layered context architecture, Context Triangle (Architectural, Local, Constraint), explicit "If Omitted" dependency auditing, concrete patterns over abstract rules, centralized `DomainError` service. | 17 passing native tests (`tests/*.test.js`) across store, authz, token, and error modules | **10 / 10** |

---

### 3. Debugging & Incident Response (`Launchpad` Pack) — **IN PROGRESS**
* **Scenario:** Production Incident Response & Triage (`linkops`)

| Module | Focus Area & Bugs Investigated | Key Fixes & Deliverables | Status / Score |
| :--- | :--- | :--- | :---: |
| **Module 01: Reading the Room (Hypothesis-First Debugging)** | Top-down triage, container health check vs config contract drift, offset pagination boundary off-by-one, non-deterministic ordering under concurrent writes. | **Bug 1:** Config contract mismatch (`DATABASE_URL`).<br>**Bug 2:** Offset boundary arithmetic (`(page - 1) * limit`).<br>**Bug 3:** Deterministic ordering (`ORDER BY id ASC`).<br>Artifacts: `progress/module-01-diagnosis.md`, `api/scripts/test_concurrent_pagination.py`. | **10 / 10** (Completed) |
| **Module 02: Reading Logs Like a Story** | Log stream analysis, structured JSON logging, correlation IDs, timezone comparison boundaries. | **Bug 3:** Log level misconfiguration & ghost errors (attached request lifecycle middleware with `X-Request-ID`).<br>**Bug 4:** Midnight timezone mismatch (end-to-end UTC normalization at schema and redirect boundaries).<br>Artifact: `progress/module-02-diagnosis.md`. | *In Progress* |

---

## 📂 Repository Structure

```text
knacklab/
├── api/                             # FastAPI Backend (LinkOps / System Design)
│   ├── app/
│   │   ├── routers/
│   │   │   ├── links.py             # CRUD endpoints: POST /links, GET /links, GET /links/{id}
│   │   │   └── redirect.py          # Public redirect: GET /r/{code} with defense-in-depth & structured logging
│   │   ├── schemas/
│   │   │   └── link.py              # Strict Pydantic v2 schemas with UTC normalization
│   │   ├── config.py                # Fail-fast settings management & log level binding
│   │   ├── db.py                    # SQLAlchemy engine & session dependency
│   │   ├── main.py                  # FastAPI app, JSON logging middleware & exception handlers
│   │   └── models.py                # Link and ClickEvent database models
│   ├── alembic/                     # Database migrations
│   ├── scripts/                     # Automated test and verification scripts
│   │   ├── test_validation_regression.py  # 12-vector URL validation regression suite
│   │   ├── test_redirect_defense.py       # Egress redirect defense-in-depth verification
│   │   ├── test_concurrent_pagination.py  # Concurrent write & pagination ordering simulation
│   │   ├── verify_module_02_logging.py    # Structured JSON request-lifecycle logging verification
│   │   ├── verify_module_02_timezone.py   # Client timezone offset normalization verification
│   │   ├── verify_api.py                  # End-to-end API test runner
│   │   └── verify-module-03.ps1           # PowerShell smoke-test drill
│   └── requirements.txt
│
├── infra/                           # Infrastructure & Containers
│   └── docker-compose.yml           # PostgreSQL & Redis container orchestration for LinkOps
│
├── worker/                          # Background Worker (LinkOps)
│   └── main.py                      # Background analytics queue consumer
│
├── src/                             # Node.js Service (AI-Augmented Engineering: Team Collaboration)
│   ├── models/
│   │   └── store.js                 # In-memory domain store (users, teams, memberships, invitations)
│   ├── routes/
│   │   └── index.js                 # Declarative route registry
│   └── services/
│       ├── authz.js                 # Role-based authorization & permission checks
│       ├── errors.js                # Centralized DomainError abstraction
│       ├── token.js                 # Timing-safe token generation & SHA-256 digest verification
│       └── workspace.js             # Workspace business logic
│
├── tests/                           # Node.js Native Test Suite (17 Passing Tests)
│   ├── authz.test.js                # RBAC and team authorization tests
│   ├── errors.test.js               # DomainError structure & serialization tests
│   ├── starter.test.js              # Route registry visibility tests
│   ├── store.test.js                # Store operations, membership, and invitation lifecycle tests
│   └── token.test.js                # Cryptographic token uniqueness & timing-safety tests
│
├── progress/                        # Learning Ledger, Evaluations & Evidence
│   ├── state.json                   # Cumulative bootcamp state machine
│   ├── eval_module_01.json          # System Design Module 01 Evaluation (10/10)
│   ├── eval_module_02.json          # System Design Module 02 Evaluation (10/10)
│   ├── eval_module_03.json          # System Design Module 03 Evaluation (10/10)
│   ├── eval_ai_module_01.json       # AI-Augmented Engineering Module 01 Evaluation (10/10)
│   ├── eval_ai_module_02.json       # AI-Augmented Engineering Module 02 Evaluation (10/10)
│   ├── eval_ai_module_03.json       # AI-Augmented Engineering Module 03 Evaluation (10/10)
│   ├── eval_debug_module_01.json    # Debugging Module 01 Evaluation (10/10)
│   ├── module-01-diagnosis.md       # Debugging Module 01 Hypothesis Log
│   ├── module-02-diagnosis.md       # Debugging Module 02 Hypothesis Log
│   ├── task-tree.md                 # 9-Task dependency tree & interface contracts
│   ├── architecture-summary.md      # Grounded workspace architecture extraction
│   ├── trust-audit.md               # Empirical verification and hallucination audit log
│   ├── ai-augmented-engineering/    # Pack-specific context bundles and contracts
│   └── evidence/                    # Captured execution traces and test logs
│
├── package.json                     # Node.js project configuration
└── README.md
```

---

## 🚀 Running Verification & Tests

### 1. Node.js Test Suite (AI-Augmented Engineering)
Run all 17 unit and integration tests using the native Node.js test runner:
```powershell
node --test tests/*.test.js
```

### 2. Python / FastAPI Test Suite (System Design & LinkOps)
Ensure dependencies and environment variables are loaded:
```powershell
# URL validation regression suite (12 attack cases: javascript:, data:, userinfo, CRLF)
$env:PYTHONPATH="api"; api\.venv\Scripts\python api\scripts\test_validation_regression.py

# Concurrent pagination & deterministic ordering stress test
$env:PYTHONPATH="api"; api\.venv\Scripts\python api\scripts\test_concurrent_pagination.py
```

### 3. Local Infrastructure (LinkOps)
Start the PostgreSQL and Redis containers for local LinkOps runtime:
```powershell
docker compose -f infra/docker-compose.yml up -d
```

---

## 🔒 Security Principles & System Invariants Enforced

1. **Perimeter Validation:** All URLs must strictly use `http://` or `https://` schemes. Userinfo (`@`), backslashes (`\`), control characters, and malformed hostnames are rejected at the Pydantic schema layer with `400 Bad Request`.
2. **Defense-in-Depth:** Destination URLs are re-checked at the redirect egress boundary; poisoned database rows return `404 Not Found` rather than redirecting to unsafe destinations.
3. **Namespace Isolation:** Public redirects live under `/r/{code}`, preventing user-generated short codes from colliding with internal administrative or health endpoints.
4. **Privacy Protection:** Client IP addresses are pseudonymized using SHA-256 before recording append-only `ClickEvent` telemetry.
5. **Cryptographic Token Safety:** Team invitation tokens use `crypto.randomBytes(32)` with timing-safe comparison (`crypto.timingSafeEqual`) and SHA-256 digest hashing to prevent database token leaks and timing side-channels.
6. **Deterministic Pagination:** Offset pagination enforces explicit tie-breaking (`ORDER BY id ASC`) to prevent phantom duplicates or missing records under concurrent insertions.
7. **Timezone Awareness:** All timestamp boundaries are normalized to timezone-aware UTC upon ingestion, preventing artificial validity dead zones across client timezones.
