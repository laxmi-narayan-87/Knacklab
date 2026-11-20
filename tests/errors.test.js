import test from "node:test";
import assert from "node:assert/strict";
import { DomainError, ERROR_CODES, isDomainError } from "../src/services/errors.js";

test("DomainError constructs with code, message, statusCode, and toJSON shape", () => {
  const err = new DomainError(ERROR_CODES.FORBIDDEN, "Access denied to resource", 403);

  assert.equal(err.code, "forbidden");
  assert.equal(err.message, "Access denied to resource");
  assert.equal(err.statusCode, 403);
  assert.equal(err.name, "DomainError");

  const json = err.toJSON();
  assert.deepEqual(json, {
    error: {
      code: "forbidden",
      message: "Access denied to resource",
    },
  });
});

test("isDomainError distinguishes domain errors from standard exceptions", () => {
  const domainErr = new DomainError(ERROR_CODES.INVALID_REQUEST, "Bad input");
  const nativeErr = new Error("Regular runtime error");

  assert.equal(isDomainError(domainErr), true);
  assert.equal(isDomainError(nativeErr), false);
  assert.equal(isDomainError(null), false);
});
