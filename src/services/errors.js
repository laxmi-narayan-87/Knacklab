export const ERROR_CODES = Object.freeze({
  INVALID_REQUEST: "invalid_request",
  UNAUTHORIZED: "unauthorized",
  FORBIDDEN: "forbidden",
  RESOURCE_NOT_FOUND: "resource_not_found",
  INTERNAL_ERROR: "internal_error",
});

export class DomainError extends Error {
  constructor(code, message, statusCode = 400) {
    super(message);
    this.name = "DomainError";
    this.code = code;
    this.statusCode = statusCode;
  }

  toJSON() {
    return {
      error: {
        code: this.code,
        message: this.message,
      },
    };
  }
}

export function isDomainError(err) {
  return Boolean(err && (err instanceof DomainError || (err.name === "DomainError" && err.code)));
}
