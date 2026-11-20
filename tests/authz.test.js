import test from "node:test";
import assert from "node:assert/strict";
import { addMembership, TEAM_ROLES } from "../src/models/store.js";
import { canUserInvite, requireTeamRole } from "../src/services/authz.js";
import { isDomainError } from "../src/services/errors.js";

const TEAM_A = "team-alpha";
const USER_OWNER = "user-owner";
const USER_ADMIN = "user-admin";
const USER_MEMBER = "user-member";
const USER_GUEST = "user-guest";
const USER_OUTSIDER = "user-outsider";

addMembership({ userId: USER_OWNER, teamId: TEAM_A, role: TEAM_ROLES.OWNER });
addMembership({ userId: USER_ADMIN, teamId: TEAM_A, role: TEAM_ROLES.ADMIN });
addMembership({ userId: USER_MEMBER, teamId: TEAM_A, role: TEAM_ROLES.MEMBER });
addMembership({ userId: USER_GUEST, teamId: TEAM_A, role: TEAM_ROLES.GUEST });

test("canUserInvite allows Owner and Admin", () => {
  assert.equal(canUserInvite(USER_OWNER, TEAM_A), true);
  assert.equal(canUserInvite(USER_ADMIN, TEAM_A), true);
});

test("canUserInvite denies Member, Guest, and Outsider", () => {
  assert.equal(canUserInvite(USER_MEMBER, TEAM_A), false);
  assert.equal(canUserInvite(USER_GUEST, TEAM_A), false);
  assert.equal(canUserInvite(USER_OUTSIDER, TEAM_A), false);
  assert.equal(canUserInvite(null, TEAM_A), false);
  assert.equal(canUserInvite(USER_OWNER, "different-team"), false);
});

test("requireTeamRole succeeds when role is authorized", () => {
  const member = requireTeamRole(USER_ADMIN, TEAM_A, [TEAM_ROLES.OWNER, TEAM_ROLES.ADMIN]);
  assert.ok(member);
  assert.equal(member.role, TEAM_ROLES.ADMIN);
});

test("requireTeamRole throws structured DomainError on unauthorized or missing membership", () => {
  try {
    requireTeamRole(USER_MEMBER, TEAM_A, [TEAM_ROLES.OWNER, TEAM_ROLES.ADMIN]);
    assert.fail("Should have thrown");
  } catch (err) {
    assert.ok(isDomainError(err));
    assert.equal(err.code, "forbidden");
    assert.equal(err.statusCode, 403);
    assert.deepEqual(err.toJSON(), {
      error: {
        code: "forbidden",
        message: "Role Member is not permitted for this action",
      },
    });
  }

  try {
    requireTeamRole(USER_OUTSIDER, TEAM_A, [TEAM_ROLES.OWNER]);
    assert.fail("Should have thrown");
  } catch (err) {
    assert.ok(isDomainError(err));
    assert.equal(err.code, "forbidden");
    assert.equal(err.statusCode, 403);
  }

  try {
    requireTeamRole(null, TEAM_A, [TEAM_ROLES.OWNER]);
    assert.fail("Should have thrown");
  } catch (err) {
    assert.ok(isDomainError(err));
    assert.equal(err.code, "unauthorized");
    assert.equal(err.statusCode, 401);
  }
});
