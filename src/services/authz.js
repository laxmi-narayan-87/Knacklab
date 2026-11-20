import { getTeamMembership, TEAM_ROLES } from "../models/store.js";

const INVITE_ROLES = new Set([TEAM_ROLES.OWNER, TEAM_ROLES.ADMIN]);

export function canUserInvite(userId, teamId) {
  if (!userId || !teamId) return false;
  const membership = getTeamMembership(userId, teamId);
  if (!membership) return false;
  return INVITE_ROLES.has(membership.role);
}

export function requireTeamRole(userId, teamId, allowedRoles = []) {
  if (!userId || !teamId) {
    throw new Error("Missing user or team context");
  }

  const membership = getTeamMembership(userId, teamId);
  if (!membership) {
    throw new Error("User does not belong to the requested team");
  }

  const allowedSet = new Set(allowedRoles);
  if (!allowedSet.has(membership.role)) {
    throw new Error(`Role ${membership.role} is not permitted for this action`);
  }

  return membership;
}
