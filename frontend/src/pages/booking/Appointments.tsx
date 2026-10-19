import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { appointmentsApi } from "../../api/appointments";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { DataTable, type Column } from "../../components/ui/DataTable";
import { FilterBar } from "../../components/ui/FilterBar";
import { Tabs } from "../../components/ui/Tabs";
import { Pagination } from "../../components/ui/Pagination";
import { StatCard } from "../../components/dashboard/StatCard";
import { EmptyState } from "../../components/ui/EmptyState";
import { useToast } from "../../hooks/useToast";
import { formatDateTime, formatStatus } from "../../utils/formatters";
import type { Appointment } from "../../types/appointments";

const columns: Column[] = [
  { key: "id", label: "ID", width: "72px" },
  {
    key: "doctor_name",
    label: "Doctor",
    render: (v, row) => String(v || row.patient_name || "—"),
  },
  { key: "status", label: "Status", render: (v) => formatStatus(String(v)) },
  { key: "appointment_type", label: "Type" },
  {
    key: "scheduled_start",
    label: "When",
    render: (v) => formatDateTime(String(v)),
  },
  {
    key: "reason_for_visit",
    label: "Reason",
    render: (v) => String(v || "—").slice(0, 60),
  },
];

export default function Appointments() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [rows, setRows] = useState<Appointment[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [tab, setTab] = useState("upcoming");
  const [stats, setStats] = useState({ total: 0, today: 0, upcoming: 0 });

  const query = useMemo(() => {
    const q: Record<string, string> = {
      page: String(page),
      ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)),
    };
    if (tab !== "all" && tab !== "upcoming" && tab !== "past") {
      q.status = tab;
    }
    return q;
  }, [filters, page, tab]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [data, dash] = await Promise.all([
        appointmentsApi.list(query),
        appointmentsApi.dashboard().catch(() => null),
      ]);
      let results = data.results ?? [];
      if (tab === "upcoming") {
        const now = Date.now();
        results = results.filter(
          (r) =>
            new Date(r.scheduled_start).getTime() >= now &&
            !["cancelled", "completed", "no_show"].includes(r.status),
        );
      } else if (tab === "past") {
        const now = Date.now();
        results = results.filter(
          (r) =>
            new Date(r.scheduled_start).getTime() < now ||
            ["completed", "cancelled", "no_show"].includes(r.status),
        );
      }
      setRows(results);
      setCount(data.count ?? results.length);
      const c = (dash as { counts?: Record<string, number> } | null)?.counts ?? {};
      setStats({
        total: Number(c.total ?? data.count ?? 0),
        today: Number(c.today ?? 0),
        upcoming: Number(c.upcoming ?? 0),
      });
    } catch {
      setRows([]);
      toast("Unable to load appointments", "error");
    } finally {
      setLoading(false);
    }
  }, [query, tab, toast]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="workspace-page">
      <PageHeader
        title="Appointments"
        subtitle="Upcoming visits, check-ins, and schedule history"
        actions={
          <>
            <Button variant="secondary" onClick={() => navigate("/waiting-list")}>
              Waiting list
            </Button>
            <Button variant="secondary" onClick={() => void load()}>
              Refresh
            </Button>
            <Button onClick={() => navigate("/discovery")}>Book visit</Button>
          <>
        }
      />
      <div className="stat-grid">
        <StatCard label="Total" value={stats.total} />
        <StatCard label="Today" value={stats.today} />
        <StatCard label="Upcoming" value={stats.upcoming} />
      </div>
      <FilterBar
        filters={[
          {
            key: "status",
            label: "Status",
            type: "select",
            options: ["", "scheduled", "confirmed", "checked_in", "completed", "cancelled"],
          },
          { key: "search", label: "Search", type: "text" },
        ]}
        values={filters}
        onChange={(v) => {
          setPage(1);
          setFilters(v);
        }}
        onReset={() => {
          setFilters({});
          setPage(1);
        }}
      />
      <Tabs
        active={tab}
        onChange={(t) => {
          setTab(t);
          setPage(1);
        }}
        tabs={[
          { id: "upcoming", label: "Upcoming" },
          { id: "confirmed", label: "Confirmed" },
          { id: "past", label: "Past" },
          { id: "all", label: "All" },
        ]}
      />
      <Card>
        {!loading && rows.length === 0 ? (
          <EmptyState
            title="No appointments"
            description="Book a visit with a CareVanta clinician."
            action={<Button onClick={() => navigate("/discovery")}>Find a doctor</Button>}
          />
        ) : (
          <DataTable
            columns={columns}
            rows={rows as unknown as Record<string, unknown>[]}
            loading={loading}
            onRowClick={(row) => navigate(`/appointments/${row.id}`)}
          />
        )}
        <Pagination page={page} pageSize={25} total={count} onPageChange={setPage} />
      </Card>
    </div>
  );
}
