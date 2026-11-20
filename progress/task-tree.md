# Team Collaboration: Atomic Task Tree & Prompt Contracts

Planning Strategy: Top-Down Decomposition (`top_down`)
Product Scenario: Team Collaboration (`team-collaboration`)
Granularity Constraint: $< 150$ lines of code change per task

---

## 1. Task Dependency Graph & Critical Path

```text
Task 1: Data Contracts (Models & Store)
  ├── Task 2: Team-Role Authorization (RBAC)
  │     └── Task 4: Create-Invitation Endpoint
  │           └── Task 7: Workflow Audit Integration
  │                 └── Task 8: Restricted Audit Log API
  │                       └── Task 9: Full Security & Regression Suite
  ├── Task 3: Token Generation & Digest Storage (Crypto)
  │     ├── Task 4: Create-Invitation Endpoint
  │     └── Task 5: Invitation Acceptance Endpoint
  │           └── Task 7: Workflow Audit Integration
  └── Task 6: Audit Event Writer (Service)
        ├── Task 7: Workflow Audit Integration
        └── Task 8: Restricted Audit Log API
```

* **Critical Path:** Task 1 $\rightarrow$ Task 2 $\rightarrow$ Task 3 $\rightarrow$ Task 4 $\rightarrow$ Task 7 $\rightarrow$ Task 8 $\rightarrow$ Task 9.

---

## 2. Complete Task Tree (9 Atomic Tasks)

### Task 1: Define Invitation and Audit Data Contracts
* **Input Context:** `src/models/store.js`, `src/services/workspace.js`, existing user/team/invitation structures, and `tests/starter.test.js`.
* **Expected Output:** Update `src/models/store.js`; add domain constants/types where needed ($< 150$ lines).
* **Acceptance Criteria:** A runtime probe can create, retrieve, and update an invitation (team ID, invited email, role, token digest, expiry, used state, timestamps). Audit records support actor, action, target, timestamp, IP, and state delta.
* **Dependencies:** None.

### Task 2: Add Team-Role Authorization Helpers (RBAC)
* **Input Context:** Task 1 output, existing team membership shape, and current route conventions.
* **Expected Output:** Authorization service module (`src/services/authz.js`) and focused tests ($< 150$ lines).
* **Acceptance Criteria:** Owner and Admin permissions are accepted for invitation creation; Member and Guest requests are rejected with `403 Forbidden`; unauthenticated requests receive `401 Unauthorized`.
* **Dependencies:** Task 1.

### Task 3: Implement Invitation Token Generation and Digest Storage
* **Input Context:** Task 1 data contract, Task 2 authorization interface, existing configuration.
* **Expected Output:** Token utility/service (`src/services/token.js`) and tests using Node's built-in `node:crypto` ($< 150$ lines).
* **Acceptance Criteria:** Generates CSPRNG tokens, stores only cryptographic digests (SHA-256), validates expiration, prevents replay attacks, and binds token to invited email.
* **Dependencies:** Tasks 1, 2.

### Task 4: Add the Create-Invitation Endpoint
* **Input Context:** Tasks 1–3, route registry (`src/routes/`), request parsing, and error conventions.
* **Expected Output:** Invitation creation route (`POST /teams/:id/invitations`) and route tests ($< 150$ lines).
* **Acceptance Criteria:** Authorized Owner/Admin receives `201 Created` with invitation response; Member/Guest receives `403 Forbidden`; invalid email/role receives `400 Bad Request`; raw token never leaked in logs or DB.
* **Dependencies:** Tasks 1, 2, 3.

### Task 5: Add Invitation Acceptance Workflow
* **Input Context:** Task 3 token verification, invitation model, user lookup, team membership records.
* **Expected Output:** Invitation acceptance route (`POST /invitations/:token/accept`) and tests ($< 150$ lines).
* **Acceptance Criteria:** Valid, unexpired token adds user to team and returns `200 OK`; expired, unknown, mismatched-email, or already-used token returns `400`/`404`/`410` without mutating membership.
* **Dependencies:** Tasks 1, 3.

### Task 6: Add Structured Audit-Event Writer
* **Input Context:** Task 1 audit contract, store/session patterns.
* **Expected Output:** Audit service (`src/services/audit.js`) and focused tests ($< 150$ lines).
* **Acceptance Criteria:** Records structured events (actor, action, target, timestamp, IP hash, delta); rejects incomplete payloads; failed actions produce no false success audit logs.
* **Dependencies:** Task 1.

### Task 7: Connect Audit Logging to Invitation Workflows
* **Input Context:** Tasks 4–6, transaction boundaries.
* **Expected Output:** Update invitation creation and acceptance to record audit entries ($< 150$ lines).
* **Acceptance Criteria:** Successful invite creation and acceptance produce corresponding audit events; rejected requests produce no success events; operations fail atomic on audit failure.
* **Dependencies:** Tasks 4, 5, 6.

### Task 8: Add Restricted Audit-Log Retrieval Endpoint
* **Input Context:** Tasks 2, 6, 7, route registry, pagination helpers.
* **Expected Output:** Admin/Owner audit route (`GET /teams/:id/audit-log`) and tests ($< 150$ lines).
* **Acceptance Criteria:** Authorized Owner/Admin receives paginated audit records filtered by team; Members, Guests, and external callers receive `403 Forbidden`.
* **Dependencies:** Tasks 2, 6, 7.

### Task 9: Complete Security and Regression Suite
* **Input Context:** All previous task outputs and existing test runner.
* **Expected Output:** Integration test suite (`tests/invitations.test.js`) and evidence report ($< 150$ lines).
* **Acceptance Criteria:** Complete coverage for unauthorized access, role escalation, invalid input, token replay, expiration, email mismatch, and audit completeness; all tests pass with `node --test`.
* **Dependencies:** Tasks 1–8.

---

## 3. Formal Interface Contracts

### Task 1 → Task 2 Interface Contract

#### Upstream (Task 1) Guarantees
`src/models/store.js` exports:
- `users`: User[]
- `teams`: Team[]
- `memberships`: Membership[]
- `invitations`: Invitation[]
- `auditEvents`: AuditEvent[]
- `TEAM_ROLES`: Object with exact values `{ OWNER: "Owner", ADMIN: "Admin", MEMBER: "Member", GUEST: "Guest" }`
- `getTeamMembership(userId, teamId) -> Membership | null`
- `addMembership({ userId, teamId, role }) -> Membership | null`

#### Record Shapes
```typescript
interface Membership {
  id: string;
  userId: string;
  teamId: string;
  role: "Owner" | "Admin" | "Member" | "Guest";
  createdAt: string; // ISO 8601
}

interface Invitation {
  id: string;
  teamId: string;
  invitedEmail: string;
  role: "Owner" | "Admin" | "Member" | "Guest";
  tokenDigest: string; // SHA-256 hex digest
  expiresAt: string;
  usedAt: string | null;
  createdAt: string;
}

interface AuditEvent {
  id: string;
  actorId: string;
  action: string;
  targetType: string;
  targetId: string;
  occurredAt: string;
  ipHash: string;
  stateDelta: Record<string, unknown>;
}
```

#### Downstream (Task 2) Consumption Rules
- `src/services/authz.js` imports `TEAM_ROLES` and `getTeamMembership`.
- Calls `getTeamMembership(userId, teamId)`.
- Evaluates `membership.role` against `TEAM_ROLES`.
- Returns `null` on missing membership (treated strictly as unauthenticated / forbidden).
- Never mutates or directly iterates the `memberships` array.

#### Shared Invariants
- Exact role string casing: `"Owner"`, `"Admin"`, `"Member"`, `"Guest"`.
- Missing records always return `null`, never throw exceptions or return undefined.
- In-memory updates maintain referential integrity.

---

## 4. Full Prompt Specifications (First 3 Sequential Tasks)

### Task 1 Prompt (Revised): Invitation, Membership & Audit Data Contracts
```markdown
Inspect src/models/store.js, src/services/workspace.js, src/routes/index.js, and tests/starter.test.js before editing.

Extend the in-memory data layer for Team Collaboration. Preserve the existing users and teams collections and add:
- memberships
- invitations
- auditEvents

Export the exact role constants (TEAM_ROLES):
- Owner
- Admin
- Member
- Guest

Export these exact helper functions:
- getTeamMembership(userId, teamId) -> Membership | null
- addMembership({ userId, teamId, role }) -> Membership | null

Record shapes required:
- Membership: id, userId, teamId, role ("Owner"|"Admin"|"Member"|"Guest"), createdAt (ISO string)
- Invitation: id, teamId, invitedEmail, role, tokenDigest, expiresAt, usedAt, createdAt
- AuditEvent: id, actorId, action, targetType, targetId, occurredAt, ipHash, stateDelta (structured object)

Behavioral rules:
- getTeamMembership() returns the matching record or null if not found.
- addMembership() creates and returns the new membership; returns null for an invalid role or duplicate (userId, teamId) pair.
- Follow the existing in-memory store pattern. Do not redesign unrelated models. Do not add external packages or HTTP routes.

Acceptance criteria:
1. memberships is exported from src/models/store.js.
2. All four role values are exported as TEAM_ROLES.
3. addMembership() creates a valid membership with an auto-generated id and createdAt.
4. getTeamMembership() returns the membership for matching userId and teamId.
5. getTeamMembership() returns null when no membership exists.
6. Duplicate memberships for the same (userId, teamId) are rejected (returns null).
7. Invalid role strings are rejected (returns null).
8. Existing tests in tests/starter.test.js still pass without error.
9. Total line changes remain strictly below 150 lines.
```

### Task 2 Prompt: Team-Role Authorization Helpers (RBAC)
```markdown
Inspect the current team and user structures in src/models/store.js and the service conventions in src/services/workspace.js. Build a small authorization helper for team actions.

Implement role checks for the existing roles:
- Owner
- Admin
- Member
- Guest

The helper must answer whether a user may perform an action such as invite_member, without trusting any role value supplied by the client. It must look up the user’s actual membership in the requested team.

Required behavior:
- Owner: may invite.
- Admin: may invite.
- Member: may not invite.
- Guest: may not invite.
- Missing user or missing team membership: return the project’s existing unauthenticated or forbidden result.
- Do not leak whether unrelated users belong to another team.

Add focused tests for every role and for a user outside the team. Do not add external packages. Do not create invitation routes or modify unrelated route behavior. Keep the change below 150 lines.
```

### Task 3 Prompt: Token Creation and Verification
```markdown
Using the invitation data contract from Task 1 and the authorization interface from Task 2, implement token creation and verification for invitations.

Use only Node’s built-in cryptographic facilities. The raw invitation token may be returned to the caller only as part of the invitation-creation response if the existing product flow requires it, but only a digest may be stored in the data store.

Required behavior:
- Generate a cryptographically strong random token.
- Store only a digest of the token.
- Verify a presented token by hashing it and comparing the digest.
- Reject unknown tokens.
- Reject expired tokens.
- Reject tokens already marked as used.
- Mark the token used only after successful acceptance, not during lookup.
- Bind verification to the invitation record and invited email.

Add tests for valid verification, invalid token, expired token, already-used token, and wrong invited email. Do not add external packages, routes, email delivery, or audit logging in this task. Keep the change below 150 lines.
```
