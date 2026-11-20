import test from "node:test";
import assert from "node:assert/strict";
import {
  generateInvitationToken,
  digestInvitationToken,
  verifyInvitationToken,
} from "../src/services/token.js";
import { isDomainError } from "../src/services/errors.js";

test("generateInvitationToken returns unique rawToken and hex digest", () => {
  const token1 = generateInvitationToken();
  const token2 = generateInvitationToken();

  assert.ok(token1.rawToken);
  assert.ok(token1.tokenDigest);
  assert.equal(token1.rawToken.length, 64);
  assert.equal(token1.tokenDigest.length, 64);
  assert.notEqual(token1.rawToken, token2.rawToken);
  assert.notEqual(token1.tokenDigest, token2.tokenDigest);
});

test("digestInvitationToken produces deterministic SHA-256 hex digest", () => {
  const raw = "test-token-fixed-string-123456";
  const digestA = digestInvitationToken(raw);
  const digestB = digestInvitationToken(raw);

  assert.equal(digestA, digestB);
  assert.equal(digestA.length, 64);
});

test("digestInvitationToken throws DomainError on malformed input", () => {
  try {
    digestInvitationToken("");
    assert.fail("Should have thrown");
  } catch (err) {
    assert.ok(isDomainError(err));
    assert.equal(err.code, "invalid_request");
    assert.equal(err.statusCode, 400);
  }
});

test("verifyInvitationToken confirms matching digest with timing safety", () => {
  const { rawToken, tokenDigest } = generateInvitationToken();

  assert.equal(verifyInvitationToken(rawToken, tokenDigest), true);
  assert.equal(verifyInvitationToken("wrong-token", tokenDigest), false);
  assert.equal(verifyInvitationToken(rawToken, "0".repeat(64)), false);
  assert.equal(verifyInvitationToken(null, tokenDigest), false);
  assert.equal(verifyInvitationToken(rawToken, null), false);
});
