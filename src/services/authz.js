import { getTeamMembership, TEAM_ROLES } from "../models/store.js";
import { DomainError, ERROR_CODES } from "./errors.js";

const INVITE_ROLES = new Set([TEAM_ROLES.OWNER, TEAM_ROLES.ADMIN]);

export function canUserInvite(userId, teamId) {
  if (!userId || !teamId) return false;
  const membership = getTeamMembership(userId, teamId);
  if (!membership) return false;
  return INVITE_ROLES.has(membership.role);
}

export function requireTeamRole(userId, teamId, allowedRoles = []) {
  if (!userId || !teamId) {
    throw new DomainError(
      ERROR_CODES.UNAUTHORIZED,
      "Missing user or team context",
      401
    );
  }

  const membership = getTeamMembership(userId, teamId);
  if (!membership) {
    throw new DomainError(
      ERROR_CODES.FORBIDDEN,
      "User does not belong to the requested team",
      403
    );
  }

  const allowedSet = new Set(allowedRoles);
  if (!allowedSet.has(membership.role)) {
    throw new DomainError(
      ERROR_CODES.FORBIDDEN,
      `Role ${membership.role} is not permitted for this action`,
      403
    );
  }

  return membership;
}
