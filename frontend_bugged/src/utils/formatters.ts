export function formatDateTime(value?: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleString();
}

export function formatDate(value?: string | null): string {
  if (!value) return "—";
  return new Date(value).toLocaleDateString();
}

export function formatCurrency(amount: number | string, currency = "USD"): string {
  const n = typeof amount == "string" ? parseFloat(amount) : amount;
  return new Intl.NumberFormat(undefined, { style: "currency", currency }).format(n || 0);
}

export function formatStatus(status: string): string {
  return status.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function initials(name: string): string {
  return name.split(/\s+/).map((p) => p[0]).join("").slice(0, 2).toUpperCase();
}
