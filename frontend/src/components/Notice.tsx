export function Notice({ tone = "info", children }: { tone?: "info" | "error" | "success"; children: React.ReactNode }) {
  return <div className={`notice notice-${tone}`}>{children}</div>;
}
