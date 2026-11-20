import test from "node:test";
import assert from "node:assert/strict";
import {
  users,
  teams,
  memberships,
  invitations,
  auditEvents,
  TEAM_ROLES,
  getTeamMembership,
  addMembership,
  createInvitation,
  getInvitationByDigest,
  markInvitationUsed,
  appendAuditEvent,
} from "../src/models/store.js";

test("store exports collections and role constants", () => {
  assert.ok(Array.isArray(users));
  assert.ok(Array.isArray(teams));
  assert.ok(Array.isArray(memberships));
  assert.ok(Array.isArray(invitations));
  assert.ok(Array.isArray(auditEvents));
  assert.equal(TEAM_ROLES.OWNER, "Owner");
  assert.equal(TEAM_ROLES.ADMIN, "Admin");
  assert.equal(TEAM_ROLES.MEMBER, "Member");
  assert.equal(TEAM_ROLES.GUEST, "Guest");
});

test("addMembership creates and retrieves a valid membership", () => {
  const membership = addMembership({
    userId: "u-1",
    teamId: "t-1",
    role: TEAM_ROLES.OWNER,
  });

  assert.ok(membership);
  assert.equal(membership.userId, "u-1");
  assert.equal(membership.teamId, "t-1");
  assert.equal(membership.role, "Owner");
  assert.ok(membership.id);
  assert.ok(membership.createdAt);

  const found = getTeamMembership("u-1", "t-1");
  assert.deepEqual(found, membership);
});

test("addMembership rejects duplicates and invalid roles", () => {
  const dup = addMembership({
    userId: "u-1",
    teamId: "t-1",
    role: TEAM_ROLES.ADMIN,
  });
  assert.equal(dup, null);

  const invalidRole = addMembership({
    userId: "u-2",
    teamId: "t-1",
    role: "SuperUser",
  });
  assert.equal(invalidRole, null);
});

test("getTeamMembership returns null for unknown pair", () => {
  assert.equal(getTeamMembership("unknown", "unknown"), null);
  assert.equal(getTeamMembership(null, "t-1"), null);
});

test("invitation creation, lookup, and mark used lifecycle", () => {
  const digest = "sha256-test-digest-12345";
  const inv = createInvitation({
    teamId: "t-1",
    invitedEmail: "dev@example.com",
    role: TEAM_ROLES.MEMBER,
    tokenDigest: digest,
  });

  assert.ok(inv);
  assert.equal(inv.invitedEmail, "dev@example.com");
  assert.equal(inv.role, "Member");
  assert.equal(inv.usedAt, null);

  const byDigest = getInvitationByDigest(digest);
  assert.deepEqual(byDigest, inv);

  assert.equal(getInvitationByDigest("non-existent"), null);

  const used = markInvitationUsed(inv.id);
  assert.ok(used.usedAt);

  // Cannot mark used twice
  assert.equal(markInvitationUsed(inv.id), null);
});

test("appendAuditEvent records structured audit entries", () => {
  const event = appendAuditEvent({
    actorId: "u-1",
    action: "team.invite_created",
    targetType: "invitation",
    targetId: "inv-1",
    ipHash: "hash-ip-123",
    stateDelta: { role: "Member" },
  });

  assert.ok(event);
  assert.equal(event.actorId, "u-1");
  assert.equal(event.action, "team.invite_created");
  assert.deepEqual(event.stateDelta, { role: "Member" });
  assert.ok(event.occurredAt);
});
