import { useCallback, useEffect, useMemo, useStat } from "react";
import { useNavigate } from "react-router-dom";
import { laboratoriesApi } from "../../api/laboratories";
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
  { key: "order_number", label: "Order #" },
  { key: "status", label: "Status", render: (v) => formatStatus(String(v ?? "")) },
  { key: "urgency", label: "Urgency" },
  { key: "ordered_at", label: "Ordered", render: (v) => (v ? formatDateTime(String(v)) : "—") },
  { key: "created_at", label: "Created", render: (v) => (v ? formatDateTime(String(v)) : "—") },
];

export default function LabOrders() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [tab, setTab] = useState("orders");
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState<Record<string, string>>({order_number: "", clinical_notes: "", urgency: ""});
  const [stats, setStats] = useState({ total: 0 });

  const query = useMemo(() => ({
    page: String(page),
    ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)),
    ...(tab !== "all" && tab !== "orders" ? { status: tab } : {}),
  }), [filters, page, tab]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await laboratoriesApi.list(query);
      setRows(data.results ?? []);
      setCount(data.count ?? 0);
      try {
        const dash = await laboratoriesApi.dashboard();
        const c = (dash as { counts?: Record<string, number> }).counts ?? {};
        setStats({ total: Number(c.total ?? data.count ?? 0) });
      } catch { /* optional */ }
    } catch {
      setRows([]);
      toast("Failed to load lab orders", "error");
    } finally {
      setLoading(false);
    }
  }, [query, toast]);

  useEffect(() => { void load(); }, [load]);

  async function save() {
    try {
      await laboratoriesApi.create(form);
      toast("Saved", "success");
      setModalOpen(false);
      setForm({order_number: "", clinical_notes: "", urgency: ""});
      void load();
    } catch {
      toast("Save failed", "error");
    }
  }

  return (
    <div className="workspace-page">
      <PageHeader
        title="Lab orders"
        subtitle="Orders, collection, and review workflow"
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
          { key: "status", label: "Status", type: "select", options: ["", "ordered", "collected", "in_progress", "results_ready", "reviewed"] },
          { key: "urgency", label: "Urgency", type: "select", options: ["", "routine", "urgent", "stat"] },
          { key: "search", label: "Search", type: "text" },
        ]}
        values={filters}
        onChange={(v) => { setPage(1); setFilters(v); }}
        onReset={() => { setFilters({}); setPage(1); }}
      />
      <Tabs active={tab} onChange={(t) => { setTab(t); setPage(1); }} tabs={[{ id: "orders", label: "Orders" }, { id: "collected", label: "Collected" }, { id: "all", label: "All" }]} />
      <Card>
        {!loading && rows.length === 0 ? (
          <EmptyState title="No records" description="Nothing matches these filters." />
        ) : (
          <DataTable
            columns={columns}
            rows={rows}
            loading={loading}
            onRowClick={(row) => navigate(`/laboratory/${row.id}`)}
          />
        )}
        <Pagination page={page} pageSize={25} total={count} onPageChange={setPage} />
      </Card>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="New Lab orders">
        <Input label="Order #" value={String(form.order_number ?? "")} onChange={(e) => setForm({ ...form, order_number: e.target.value })} />
        <Textarea label="Clinical notes" rows={3} value={String(form.clinical_notes ?? "")} onChange={(e) => setForm({ ...form, clinical_notes: e.target.value })} />
        <Select label="Urgency" value={String(form.urgency ?? "")} onChange={(e) => setForm({ ...form, urgency: e.target.value })} options={["routine", "urgent", "stat"]} />
        <div className="modal-actions">
          <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
          <Button onClick={() => void save()}>Save</Button>
        </div>
      </Modal>
    </div>
  );
}
