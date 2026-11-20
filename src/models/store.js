import crypto from "node:crypto";

export const users = [];
export const teams = [];
export const memberships = [];
export const invitations = [];
export const auditEvents = [];

export const TEAM_ROLES = Object.freeze({
  OWNER: "Owner",
  ADMIN: "Admin",
  MEMBER: "Member",
  GUEST: "Guest",
});

const VALID_ROLES = new Set(Object.values(TEAM_ROLES));

export function getTeamMembership(userId, teamId) {
  if (!userId || !teamId) return null;
  return memberships.find((m) => m.userId === userId && m.teamId === teamId) || null;
}

export function addMembership({ userId, teamId, role }) {
  if (!userId || !teamId || !VALID_ROLES.has(role)) return null;
  if (getTeamMembership(userId, teamId)) return null;

  const record = {
    id: crypto.randomUUID(),
    userId,
    teamId,
    role,
    createdAt: new Date().toISOString(),
  };
  memberships.push(record);
  return record;
}

export function createInvitation({ teamId, invitedEmail, role, tokenDigest, expiresAt }) {
  if (!teamId || !invitedEmail || !VALID_ROLES.has(role) || !tokenDigest) return null;

  const record = {
    id: crypto.randomUUID(),
    teamId,
    invitedEmail: invitedEmail.toLowerCase().trim(),
    role,
    tokenDigest,
    expiresAt: expiresAt || new Date(Date.now() + 7 * 24 * 60 * 60 * 1000).toISOString(),
    usedAt: null,
    createdAt: new Date().toISOString(),
  };
  invitations.push(record);
  return record;
}

export function getInvitationByDigest(tokenDigest) {
  if (!tokenDigest) return null;
  return invitations.find((inv) => inv.tokenDigest === tokenDigest) || null;
}

export function markInvitationUsed(invitationId, acceptedAt = new Date().toISOString()) {
  const inv = invitations.find((i) => i.id === invitationId);
  if (!inv || inv.usedAt) return null;
  inv.usedAt = acceptedAt;
  return inv;
}

export function appendAuditEvent({ actorId, action, targetType, targetId, ipHash, stateDelta }) {
  if (!actorId || !action || !targetType || !targetId) return null;

  const event = {
    id: crypto.randomUUID(),
    actorId,
    action,
    targetType,
    targetId,
    occurredAt: new Date().toISOString(),
    ipHash: ipHash || "anonymous",
    stateDelta: stateDelta || {},
  };
  auditEvents.push(event);
  return event;
}
