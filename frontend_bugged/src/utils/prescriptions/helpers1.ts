export function formatDosage(dosage: string, frequency: string): string {
  return `${dosage} · ${frequency}`;
}
export function refillsLabel(remaining: number, allowed: number): string {
  return `${remaining} of ${allowed} refills left`;
}
export function hasWarnings(rx: { has_interaction_warnings?: boolean }): boolean {
  return Boolean(rx.has_interaction_warnings);
}
