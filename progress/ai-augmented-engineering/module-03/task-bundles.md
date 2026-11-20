# Per-Task Context Bundles (Tasks 1–3)

---

## Task 1: Foundational Data Contracts & Store Accessors

### 1. Files to Read (with "If Omitted" Risk)
1. `src/models/store.js`
   * *Reason:* Reveals existing in-memory arrays (`users`, `teams`, `invitations`) and ESM export style.
   * *If Omitted:* Agent may overwrite existing collections, invent incompatible naming schemes, or introduce an external database library.
2. `src/services/workspace.js`
   * *Reason:* Demonstrates baseline service export conventions and workspace assumptions.
   * *If Omitted:* Agent may misjudge module boundaries or export patterns.
3. `tests/starter.test.js`
   * *Reason:* Demonstrates native Node test runner imports (`node:test`, `node:assert/strict`).
   * *If Omitted:* Agent may write tests using Jest, Mocha, or unsupported syntax.

### 2. Files to Modify / Create
* `src/models/store.js` (Modify: add `memberships`, `auditEvents`, `TEAM_ROLES`, accessors)
* `tests/store.test.js` (Create: unit & contract test suite for storage layer)

### 3. Expected Output
* Exports: `users`, `teams`, `memberships`, `invitations`, `auditEvents`, `TEAM_ROLES`
* Functions: `getTeamMembership`, `addMembership`, `createInvitation`, `getInvitationByDigest`, `markInvitationUsed`, `appendAuditEvent`
* Line Budget: $< 150$ lines of change.

---

## Task 2: Team-Role Authorization (RBAC)

### 1. Files to Read (with "If Omitted" Risk)
1. `src/models/store.js`
   * *Reason:* Provides `TEAM_ROLES` constants and `getTeamMembership(userId, teamId)` contract.
   * *If Omitted:* Agent will invent a non-existent `team_members` table or invent arbitrary role strings, triggering decomposition failure.
2. `tests/store.test.js`
   * *Reason:* Confirms actual runtime behavior of `getTeamMembership()` (specifically returning `null` when a membership does not exist).
   * *If Omitted:* Agent may assume exceptions are thrown or write redundant defensive code.
3. `tests/starter.test.js`
   * *Reason:* Establishes standard assertion and test naming conventions.
   * *If Omitted:* Agent may drift from project test standards.

### 2. Files to Modify / Create
* `src/services/authz.js` (Create)
* `tests/authz.test.js` (Create)

### 3. Expected Output
* Exports:
  * `canUserInvite(userId, teamId) -> boolean`
  * `requireTeamRole(userId, teamId, allowedRoles) -> Membership`
* Rules: Enforces `Owner` and `Admin` permissions; rejects `Member`, `Guest`, and non-members (`null`).
* Line Budget: $< 150$ lines of change.

---

## Task 3: Token Generation & Verification (Crypto)

### 1. Files to Read (with "If Omitted" Risk)
1. `package.json`
   * *Reason:* Confirms `"type": "module"` and absence of external token libraries (forcing use of `node:crypto`).
   * *If Omitted:* Agent may attempt `npm install uuid` or `jsonwebtoken` or use `require()`.
2. `src/models/store.js`
   * *Reason:* Details the `tokenDigest` field format and `getInvitationByDigest` accessor.
   * *If Omitted:* Agent may store plaintext tokens or use mismatched hashing algorithms.
3. `tests/store.test.js`
   * *Reason:* Confirms the shape of invitation records expected by store accessors.
   * *If Omitted:* Agent may return incompatible object wrappers.

### 2. Files to Modify / Create
* `src/services/token.js` (Create)
* `tests/token.test.js` (Create)

### 3. Expected Output
* Exports:
  * `generateInvitationToken() -> { rawToken: string, tokenDigest: string }`
  * `digestInvitationToken(rawToken: string) -> string`
  * `verifyInvitationToken(rawToken: string, expectedDigest: string) -> boolean`
* Cryptography: Uses `node:crypto` (`randomBytes(32).toString('hex')` and `createHash('sha256')`).
* Line Budget: $< 150$ lines of change.
