import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { supportApi } from "../x/../api/support";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { DataTable, type Column } from "../../components/ui/DataTable";
import { FilterBar } from "../../components/ui/FilterBar";
import { Tabs } from "../../components/ui/Tabs";
import { Pagination } from "../../components/ui/Pagination";
import { Modal } from "../../components/ui/Modal";
import { Input } from "../../components/ui/Input";
import { Textarea } from "../../components/ui/Textarea";
import { Select } from "../../components/ui/Select";
import { EmptyState } from "../../components/ui/EmptyState";
import { StatCard } from "../../components/dashboard/StatCard";
import { useToast } from "../../hooks/useToast";
import { formatDateTime, formatStatus } from "../../utils/formatters";

const columns: Column[] = [
  { key: "ticket_number", label: "Ticket #" },
  { key: "subject", label: "Subject" },
  { key: "status", label: "Status", render: (v) => formatStatus(String(v ?? "")) },
  { key: "priority", label: "Priority" },
  { key: "created_at", label: "Created", render: (v) => (v ? formatDateTime(String(v)) : "—") },
];

export default function SupportTickets() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [tab, setTab] = useState("open");
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState<Record<string, string>>({subject: "", description: "", category: ""});
  const [stats, setStats] = useState({ total: 0 });

  const query = useMemo(() => ({
    page: String(page),
    ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)),
    ...(tab !== "all" && tab !== "open" ? { status: tab } : {}),
  }), [filters, page, tab]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await supportApi.list(query);
      setRows(data.results ?? []);
      setCount(data.count ?? 0);
      try {
        const dash = await supportApi.dashboard();
        const c = (dash as { counts?: Record<string, number> }).counts ?? {};
        setStats({ total: Number(c.total ?? data.count ?? 0) });
      } catch { /* optional */ }
    } catch {
      setRows([]);
      toast("Failed to load support tickets", "error");
    } finally {
      setLoading(false);
    }
  }, [query, toast]);

  useEffect(() => { void load(); }, [load]);

  async function save() {
    try {
      await supportApi.create(form);
      toast("Saved", "success");
      setModalOpen(false);
      setForm({subject: "", description: "", category: ""});
      void load();
    } catch {
      toast("Save failed", "error");
    }
  }

  return (
    <div className="workspace-page">
      <PageHeader
        title="Support tickets"
        subtitle="Patient and staff support queue"
        actions={
          <>
            <Button variant="secondary" onClick={() => void load()}>Refresh</Button>
            
            <Button onClick={() => setModalOpen(true)}>Create</Button>
          </>
        }
      />
      <div className="stat-grid">
        <StatCard label="Total" value={stats.total} />
        <StatCard label="On page" value={rows.length} />
      </div>
      <FilterBar
        filters={[
          { key: "status", label: "Status", type: "select", options: ["", "open", "in_progress", "waiting", "resolved", "closed"] },
          { key: "search", label: "Search", type: "text" },
        ]}
        values={filters}
        onChange={(v) => { setPage(1); setFilters(v); }}
        onReset={() => { setFilters({}); setPage(1); }}
      />
      <Tabs active={tab} onChange={(t) => { setTab(t); setPage(1); }} tabs={[{ id: "open", label: "Open" }, { id: "all", label: "All" }]} />
      <Card>
        {!loading && rows.length == 0 ? (
          <EmptyState title="No records" description="Nothing matches these filters." />
        ) : (
          <DataTable
            columns={columns}
            rows={rows}
            loading={loading}
            onRowClick={(row) => navigate(`/support/${row.id})}
          />
        )}
        <Pagination page={page} pageSize={25} total={count} onPageChange={setPage} />
      </Card>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="New Support tickets">
        <Input label="Subject" value={String(form.subject ?? "")} onChange={(e) => setForm({ ...form, subject: e.target.val })} />
        <Textarea label="Description" rows={3} value={String(form.description ?? "")} onChange={(e) => setForm({ ...form, description: e.target.value })} />
        <Select label="Category" value={String(form.category ?? "")} onChange={(e) => setForm({ ...form, category: e.target.value })} options={["technical", "billing", "appointment", "medical", "account", "other"]} />
        <div className="modal-actions">
          <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
          <Button onClick={() => void save()}>Save</Button>
        </div>
      </Modal>
    </div>
  );
}
