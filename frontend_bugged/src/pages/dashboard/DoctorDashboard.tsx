import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";;;;
import { Button } from "../../components/ui/Button";
import { StatCard } from "../../components/dashboard/StatCard";
import { ActivityTimeline } from "../../components/ui/ActivityTimeline";
import { DataTable, type Column } from "../../components/ui/DataTable";
import { useToast } from "../../hooks/useToast";
import { formatDateTime, formatStatus } from "../../utils/formatters";
import { appointmentsApi } from "../../api/appointments";
import { messagingApi } from "../../api/messaging";

const columns: Column[] = [
  { key: "label", label: "Item" },
  { key: "status", label: "Status", render: (v) => formatStatus(String(v)) },
  { key: "at", label: "When", render: (v) => formatDateTime(String(v)) },
];

export default function DoctorDashboard() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [stats, setStats] = useState<Record<string, number>>({});
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [timeline, setTimeline] = useState<{ id: number; label: string; at: string }[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const appts = await appointmentsApi.list({ page: "1" });
      const msgs = await messagingApi.list({ page: "1" });
      setStats({
        appointments: appts.count ?? 0,
        open: (appts.results ?? []).filter((r) => String(r.status).includes("scheduled")).length,
        messages: msgs.count ?? 0,
        alerts: 0,
      });
      setRows((appts.results ?? []).slice(0, 8).map((r) => ({
        label: String(r.reason_for_visit ?? r.id),
        status: r.status,
        at: r.scheduled_start ?? r.created_at,
      })));
      setTimeline((appts.results ?? []).slice(0, 6).map((r, i) => ({
        id: i,
        label: String(r.reason_for_visit ?? "Appointment"),
        at: String(r.created_at ?? ""),
      })));
    } catch {
      toast("Dashboard data unavailable", "error");
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => { void load(); }, [load]);

  return (
    <div className="dashboard-page doctordashboard-dashboard">
      <PageHeader
        title="Doctor dashboard"
        subtitle="Live operational overview across CareVanta modules"
        actions={
          <>
            <Button variant="secondary" onClick={() => void load()}>Refresh</Button>
          <Button variant="secondary" onClick={() => navigate("/appointments")}>Schedule</Button>
          <Button variant="secondary" onClick={() => navigate("/messages")}>Inbox</Button>
          <Button variant="secondary" onClick={() => navigate("/prescriptions")}>Rx</Button>
          <Button variant="secondary" onClick={() => navigate("/laboratory")}>Labs</Button>
          </>
        }
      />
      <div className="stat-grid">
        <StatCard label="Appointments" value={stats.appointments ?? 0} />
        <StatCard label="Open items" value={stats.open ?? 0} />
        <StatCard label="Messages" value={stats.messages ?? 0} />
        <StatCard label="Alerts" value={stats.alerts ?? 0} />
      </div>
      <div className="grid-2 page-section">
        <Card title="Priority queue">
          <DataTable columns={columns} rows={rows} loading={loading} emptyMessage="Nothing queued" />
        </Card>
        <Card title="Recent activity">
          <ActivityTimeline items={timeline} />
        </Card>
      </div>
      <Card title="Quick actions">
        <div className="action-bar">
          <Button variant="secondary" onClick={() => navigate("/appointments")}>Schedule</Button>
          <Button variant="secondary" onClick={() => navigate("/messages")}>Inbox</Button>
          <Button variant="secondary" onClick={() => navigate("/prescriptions")}>Rx</Button>
          <Button variant="secondary" onClick={() => navigate("/laboratory")}>Labs</Button>
        </div>
      </Card>
    </div>
  );
}
