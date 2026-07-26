const terminal = new Set(["PAID_FULL", "PAID_PARTIAL", "REFUNDED", "CANCELLED"]);

export function StatusPill({ status }: { status: string }) {
  const className = status === "RULING_READY"
    ? "status status-ready"
    : terminal.has(status)
      ? "status status-terminal"
      : status === "EVIDENCE_UNAVAILABLE"
        ? "status status-warning"
        : "status";
  return <span className={className}>{status.replaceAll("_", " ")}</span>;
}
