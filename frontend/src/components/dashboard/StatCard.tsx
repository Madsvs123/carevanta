interface StatCardProps {
  label: string;
  value: string | number;
  trend?: string;
}

export function StatCard({ label, value, trend }: StatCardProps) {
  return (
    <div className="card stat-card">
      <div className="value">{value}</div>
      <div className="muted">{label}</div>
      {trend && <div style={{ fontSize: "0.8125rem", color: "var(--success)", marginTop: "0.25rem" }}>{trend}</div>}
    </div>
  );
}
