# TaskFlow API: Architecture Summary & Extension Points

Generated: 2026-11-19
Product Scenario: Team Collaboration (`team-collaboration`)

---

## Part 1: Architecture Summary

### 1. Top-Level Folder Structure & Directory Responsibilities
* `src/`: Core application source code.
  * `src/models/`: In-memory and entity domain collections. Currently houses `store.js`.
  * `src/routes/`: Route declarations and API handlers. Currently houses `index.js`.
  * `src/services/`: Business logic, workspace metadata, and domain operations. Currently houses `workspace.js`.
* `tests/`: Automated test suites executed via Node.js native test runner (`node --test`). Currently houses `starter.test.js`.
* `progress/`: Learning milestone tracking, evidence capture, and architectural design artifacts.
* `package.json`: Application metadata, ECMAScript module configuration (`"type": "module"`), and test scripts.
* `api/`: Companion FastAPI backend from System Design Launchpad foundation (`api/app/`).

### 2. Data Models, Fields & State Persistence
* **Entities & Fields:**
  * `users`: `[]` (in-memory array collection in `src/models/store.js#L1`).
  * `teams`: `[]` (in-memory array collection in `src/models/store.js#L2`).
  * `invitations`: `[]` (in-memory array collection in `src/models/store.js#L3`).
* **State Lifecycle:** Purely in-memory at this starter stage. State does not persist across process restarts. Relationships are unindexed arrays.
* **Database / Migrations:** No relational or document database is wired into `src/models/store.js` yet (unlike the `api/` PostgreSQL database).

### 3. API Routes, Methods & Request/Response Behavior
* `GET /health`: Health check endpoint listed in `src/routes/index.js#L2`.
* `GET /teams`: Team listing endpoint listed in `src/routes/index.js#L2`.
* **Behavior:** Defined declaratively via `listRoutes()` returning `["GET /health", "GET /teams"]`. HTTP listener server is not yet instantiated.

### 4. Authentication, Authorization & Middleware
* **Current State:** None implemented in `src/routes/index.js`.
* **Missing Enforcement:** No token extraction, no session lookup, no role checks (`Owner`, `Admin`, `Member`, `Guest`). All routes are currently unauthenticated.

### 5. Existing Tests & Verified Invariants
* `tests/starter.test.js#L4-L6`: Executes `assert.deepEqual(listRoutes(), ["GET /health", "GET /teams"])`. Verified passing via `node --test tests/starter.test.js`.

---

## Part 2: Extension Points Analysis (Team Collaboration Feature)

### 1. Route Extension (`src/routes/`)
* **Existing Pattern:** Declarative array listing in `src/routes/index.js`.
* **Extension Plan:** 
  * Add dedicated route modules (e.g. `src/routes/teams.js` and `src/routes/invitations.js`).
  * Register `POST /teams/:id/invitations` (create invitation) and `POST /invitations/:token/accept` (accept invitation).
* **Architectural Risk:** Monolithic route file risk if all invitation handling is dumped directly into `src/routes/index.js`.

### 2. Data Model Extension (`src/models/`)
* **Existing Pattern:** Exported domain arrays in `src/models/store.js`.
* **Extension Plan:**
  * Define explicit entity shapes for `Invitation`: `{ id, teamId, email, role, token, status, expiresAt, invitedBy, createdAt }`.
  * Ensure status tracking (`"pending"`, `"accepted"`, `"expired"`, `"revoked"`).
* **Architectural Risk:** Unbounded in-memory arrays lack atomic concurrency locks, uniqueness constraints, and foreign key cascades.

### 3. Request Validation & Middleware
* **Existing Pattern:** No formal validation pipeline exists in the JavaScript starter.
* **Extension Plan:** Implement schema-based validation for request payloads (validating email syntax, role allowlist, team existence, and non-empty inputs).
* **Architectural Risk:** Without validation middleware, malformed inputs or privilege escalation payloads could bypass route logic.

### 4. Authentication & Authorization Guardrails
* **Existing Pattern:** Unauthenticated.
* **Extension Plan:**
  * Introduce an authentication context (`req.user`).
  * Implement RBAC checks: only `Owner` or `Admin` can create invitations; members and guests must receive `403 Forbidden`.
* **Architectural Risk:** Broken object-level authorization (IDOR) if a user invites members to a team they do not manage.

### 5. Asynchronous & Background Work
* **Existing Pattern:** No event loop queues or worker processes configured.
* **Extension Plan:** Invitation notification delivery (emails/notifications) and audit event emission should be queued or handled via async hooks without blocking the HTTP response.

### 6. Test Placement (`tests/`)
* **Existing Pattern:** `tests/*.test.js` using `node:test` and `node:assert/strict`.
* **Extension Plan:** Add `tests/invitations.test.js` testing:
  * Happy path invitation creation by Admin.
  * Rejection of unauthorized roles (`Member`/`Guest` $\rightarrow$ 403).
  * One-time use token enforcement (replay attack prevention).
  * Expiration validation.
  * Target email matching on acceptance.
