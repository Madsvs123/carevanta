export function invoiceStatusColor(status: string): string {
  const map: Record<string, string> = { paid: "success", pending: "warning", overdue: "danger" };
  return map[status] ?? "default";
}
export function sumLineItems(items: { total?: number | string }[]): number {
  return items.reduce((s, i) => s + Number(i.total ?? 0), 0);
}
