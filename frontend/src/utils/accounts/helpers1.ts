export function validateEmail(email: string): boolean {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
export function passwordStrength(pw: string): "weak" | "medium" | "strong" {
  if (pw.length < 8) return "weak";
  if (/[A-Z]/.test(pw) && /[0-9]/.test(pw) && pw.length >= 12) return "strong";
  return "medium";
}
export function roleLabel(role: string): string {
  return role.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}
