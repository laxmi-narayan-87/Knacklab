import crypto from "node:crypto";

export function digestInvitationToken(rawToken) {
  if (!rawToken || typeof rawToken !== "string") {
    throw new Error("Invalid raw token provided");
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
