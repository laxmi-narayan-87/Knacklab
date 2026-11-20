# System-Level Architecture & Constraints Document
**Project:** TaskFlow API Starter (Team Collaboration Feature)
**Runtime:** Node.js v22.x LTS (ECMAScript Modules, `"type": "module"` in `package.json`)

---

## 1. Directory Structure & Module Responsibilities

* `src/models/`: In-memory collections, domain constants, record shapes, and safe accessors. Callers must use exported accessors and never mutate arrays directly.
* `src/services/`: Pure business logic and domain operations (RBAC authorization, cryptographic token handling, audit event logging). Services consume model accessors.
* `src/routes/`: HTTP route handlers, request validation, status-code mapping, and JSON response serialization.
* `tests/`: Automated unit and integration tests run via Node's native test runner (`node --test tests/*.test.js`).
* `progress/`: Evaluation records, learning artifacts, and task specifications. Never imported by application code.

---

## 2. Standard API Error Response Contract

All endpoint errors must strictly conform to this JSON schema:

```json
{
  "error": {
    "code": "invalid_request",
    "message": "Human-readable explanation of the validation or domain error."
  }
}
```

### HTTP Status Code Mapping:
* `400 Bad Request` (`code: "invalid_request"` | `"validation_error"`): Malformed input, missing fields, invalid role strings, or expired tokens.
* `401 Unauthorized` (`code: "unauthorized"`): Missing or invalid authentication credentials.
* `403 Forbidden` (`code: "forbidden"`): Authenticated user lacks required team privileges (e.g., Member/Guest attempting an invitation).
* `404 Not Found` (`code: "resource_not_found"`): Missing team, missing user, or unknown token (where token existence should not be disclosed).
* `500 Internal Server Error` (`code: "internal_error"`): Unhandled server exceptions; must never leak stack traces, database internals, or raw tokens.

---

## 3. Universal Guardrails & Non-Negotiable Constraints

1. **Zero External Dependencies:** Use only Node.js v22 built-in modules (`node:crypto`, `node:test`, `node:assert/strict`). Do not install new npm packages.
2. **ESM Compliance:** Use standard `import` / `export` syntax with explicit `.js` extensions on relative imports.
3. **Storage Encapsulation:** Do not mutate exported store arrays directly outside `src/models/store.js`. Always invoke exported accessors (`getTeamMembership`, `addMembership`, etc.).
4. **Token Security:** Raw invitation tokens must NEVER be persisted to storage or written to log streams. Store only cryptographic SHA-256 digests.
5. **Exact Interface Compliance:** Implement exact function names, argument signatures, and return shapes defined in the task contracts. Missing records must return `null`, never throw exceptions or return `undefined`.
6. **Task Granularity:** Each task implementation must strictly stay below 150 lines of code changes.
7. **Empirical Verification:** Every task must include dedicated tests covering success paths, negative paths, boundary inputs, and security edge cases.
