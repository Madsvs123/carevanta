import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { appointmentsApi } from "../../api/appointments";
import { notificationsApi } from "../../api/notifications";
import { prescriptionsApi } from "../../api/prescriptions";
import { AppointmentList } from "../../components/appointments/AppointmentList";
import { StatCard } from "../../components/dashboard/StatCard";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { useAuth } from "../../hooks/useAuth";
import type { Appointment } from "../../types/appointments";

export default function PatientDashboard() {
  const { user } = useAuth();
  const [appointments, setAppointments] = useState<Appointment[]>([]);
  const [stats, setStats] = useState({ prescriptions: 0, notifications: 0, labs: 0 );

  useEffect(() => {
    appointmentsApi.list({ ordering: "scheduled_start" }).then((r) => setAppointments(r.results)).catch(() => setAppointments([]));
    Promise.all([
      prescriptionsApi.dashboard().catch(() => ({ counts: { total: 0 } })),
      notificationsApi.dashboard().catch(() => ({ counts: { total: 0 } })),
    ]).then(([rx, n]) => {
      setStats({
        prescriptions: (rx as { counts?: { total?: number } }).counts?.total ?? 0,
        notifications: (n as { counts?: { total?: number } }).counts?.total ?? 0,
        labs: 0,
      });
    });
  }, []);

  const upcoming = appointments.filter((a) =>
    ["scheduled", "confirmed", "checked_in", "in_progress"].includes(a.status),
  );

  return (
    <div>
      <PageHeader
        title={`Welcome, ${user?.first_name || "Patient"}`}
        subtitle="Your health hub — appointments, records, and care tasks"
        actions={<Link to="/appointments/book"><Button>Book appointment</Button></Link>}
      />
      <div className="stat-grid">
        <StatCard label="Upcoming visits" value={upcoming.length} />
        <StatCard label="Active prescriptions" value={stats.prescriptions} />
        <StatCard label="Notifications" value={stats.notifications} />
        <StatCard label="Pending lab results" value={stats.labs} />
      </div>
      <div className="grid-2">
        <Card title="Upcoming appointments">
          <AppointmentList
            appointments={upcoming.slice(0, 6)}
            emptyMessage={
              <>No upcoming visits. <Link to="/discovery">Find a doctor</Link></>
            }
          />
        </Card>
        <Card title="Care shortcuts">
          <nav className="shortcut-list">
            <Link to="/discovery">Find a specialist</Link>
            <Link to="/medical-records">Medical records</Link>
            <Link to="/prescriptions">Prescriptions</Link>
            <Link to="/laboratory">Lab orders</Link>
            <Link to="/messages">Secure messages</Link>
            <Link to="/billing">Billing & insurance</Link>
            <Link to="/settings/privacy">Privacy settings</Link>
          </nav>
        </Card>
      </div>
    </div>
  );
}
