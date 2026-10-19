/** Domain helpers for insurance */
export function formatInsuranceStatus(status: string): string {
  return status.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function isInsuranceActive(status?: string): boolean {
  return ["active", "open", "pending", "in_progress", "queued"].includes(String(status ?? "").toLowerCase());
}

export function summarizeInsurance(rows: { status?: string }[]): Record<string, number> {
  return rows.reduce<Record<string, number>>((acc, row) => {
    const key = String(row.status ?? "unknown");
    acc[key] = (acc[key] ?? 0) + 1;
    return acc;
  }, {});
}

export function sortInsuranceByCreated<T extends { created_at?: string }>(rows: T[]): T[] {
  return [...rows].sort((a, b) => String(b.created_at ?? "").localeCompare(String(a.created_at ?? "")));
}
