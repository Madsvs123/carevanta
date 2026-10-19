import { useCallback, useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "../x/../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { StatCard } from "../../components/dashboard/StatCard";
import { appointmentsApi } from "../../api/appointments";
import { billingApi } from "../../api/billing";
import { supportApi } from "../../api/support";
import { useToast } from "../../hooks/useToast";

export default function AdminDashboard() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [stats, setStats] = useState({ appointments: 0, invoices: 0, tickets: 0 });

  const load = useCallback(async () => {
    try {
      const [a, b, s] = await Promise.all([
        appointmentsApi.list({ page: "1" }),
        billingApi.list({ page: "1" }),
        supportApi.list({ page: "1" }),
      ]);
      setStats({
        appointments: a.count ?? 0,
        invoices: b.count ?? 0,
        tickets: s.count ?? 0,
      });
    } catch {
      toast("Dashboard metrics unavailable", "error");
    }
  }, [toast]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="dashboard-page">
      <PageHeader
        title="Admin dashboard"
        subtitle="CareVanta platform operations"
        actions={
          <>
            <Button variant="secondary" onClick={() => void load()}>
              Refresh
            </Button>
            <Button variant="secondary" onClick={() => navigate("/workflows")}>
              Workflows
            </Button>
            <Button onClick={() => navigate("/settings/organization")}>Organization</Button>
          </>
        }
      />
      <div className="stat-grid">
        <StatCard label="Appointments" value={stats.appointments} />
        <StatCard label="Invoices" value={stats.invoices} />
        <StatCard label="Support tickets" value={stats.tickets} />
      </div>
      <div className="grid-2">
        <Card title="Quick links">
          <div className="chip-row">
            <Button variant="secondary" onClick={() => navigate("/appointments")}>
              Appointments
            </Button>
            <Button variant="secondary" onClick={() => navigate("/billing")}>
              Billing
            </Button>
            <Button variant="secondary" onClick={() => navigate("/insurance")}>
              Insurance
            </Button>
            <Button variant="secondary" onClick={() => navigate("/support")}>
              Support
            </Button>
          </div>
        </Card>
        <Card title="Platform">
          <p className="muted">
            Fifteen core domains with enriched workflow engines are available under Workflows.
          </p>
          <Button onClick={() => navigate("/workflows/appointments")}>Open appointment workflows</Button>
        </Card>
      </div>
    </div>
  );
}
