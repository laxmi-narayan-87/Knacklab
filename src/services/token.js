import crypto from "node:crypto";
import { DomainError, ERROR_CODES } from "./errors.js";

export function digestInvitationToken(rawToken) {
  if (!rawToken || typeof rawToken !== "string") {
    throw new DomainError(
      ERROR_CODES.INVALID_REQUEST,
      "Invalid raw token provided",
      400
    );
  }
  return crypto.createHash("sha256").update(rawToken).digest("hex");
}

export function generateInvitationToken() {
  const rawToken = crypto.randomBytes(32).toString("hex");
  const tokenDigest = digestInvitationToken(rawToken);
  return { rawToken, tokenDigest };
}

export function verifyInvitationToken(rawToken, expectedDigest) {
  if (!rawToken || !expectedDigest || typeof rawToken !== "string" || typeof expectedDigest !== "string") {
    return false;
  }

  const computedDigest = digestInvitationToken(rawToken);
  if (computedDigest.length !== expectedDigest.length) {
    return false;
  }

  return crypto.timingSafeEqual(
    Buffer.from(computedDigest, "hex"),
    Buffer.from(expectedDigest, "hex")
  );
}
