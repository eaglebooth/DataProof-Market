export function shortAddress(value: string) {
  return value.length > 12 ? `${value.slice(0, 6)}...${value.slice(-4)}` : value;
}

export function compactDigest(value: string) {
  return value.length > 26 ? `${value.slice(0, 14)}...${value.slice(-8)}` : value;
}

export function parseJsonResult<T>(value: unknown): T {
  if (typeof value === "string") return JSON.parse(value) as T;
  if (value && typeof value === "object") {
    const record = value as Record<string, unknown>;
    for (const key of ["result", "data", "returnValue", "decoded"]) {
      if (record[key] !== undefined) return parseJsonResult<T>(record[key]);
    }
  }
  throw new Error("The contract returned an unreadable response.");
}
