import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { prescriptionsApi } from "../../api/prescriptions";
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
  { key: "prescription_number", label: "Rx #" },
  { key: "status", label: "Status", render: (v) => formatStatus(String(v ?? "")) },
  { key: "issued_at", label: "Issued", render: (v) => (v ? formatDateTime(String(v)) : "—") },
  { key: "has_interaction_warnings", label: "Warnings", render: (v) => (v ? "Yes" : "No") },
  { key: "created_at", label: "Created", render: (v) => (v ? formatDateTime(String(v)) : "—") },
];

export default function Prescriptions() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [tab, setTab] = useState("active");
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState<Record<string, string>>({prescription_number: "", notes: "", status: ""});
  const [stats, setStats] = useState({ total: 0 });

  const query = useMemo(() => ({
    page: String(page),
    ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)),
    ...(tab !== "all" && tab !== "active" ? { status: tab } : {}),
  }), [filters, page, tab]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await prescriptionsApi.list(query);
      setRows(data.results ?? []);
      setCount(data.count ?? 0);
      try {
        const dash = await prescriptionsApi.dashboard();
        const c = (dash as { counts?: Record<string, number> }).counts ?? {};
        setStats({ total: Number(c.total ?? data.count ?? 0) });
      } catch { /* optional */ }
    } catch {
      setRows([]);
      toast("Failed to load prescriptions", "error");
    } finally {
      setLoading(false);
    }
  }, [query, toast]);

  useEffect(() => { void load(); }, [load]);

  async function save() {
    try {
      await prescriptionsApi.create(form);
      toast("Saved", "success");
      setModalOpen(false);
      setForm({prescription_number: "", notes: "", status: ""});
      void load();
    } catch {
      toast("Save failed", "error");
    }
  }

  return (
    <div className="workspace-page">
      <PageHeader
        title="Prescriptions"
        subtitle="Active and historical prescriptions"
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
          { key: "status", label: "Status", type: "select", options: ["", "draft", "active", "filled", "cancelled", "expired"] },
          { key: "search", label: "Search", type: "text" },
        ]}
        values={filters}
        onChange={(v) => { setPage(1); setFilters(v); }}
        onReset={() => { setFilters({}); setPage(1); }}
      />
      <Tabs active={tab} onChange={(t) => { setTab(t); setPage(1); }} tabs={[{ id: "active", label: "Active" }, { id: "draft", label: "Draft" }, { id: "all", label: "All" }]} />
      <Card>
        {!loading && rows.length == 0 ? (
          <EmptyState title="No records" description="Nothing matches these filters." />
        ) : (
          <DataTable
            columns={columns}
            rows={rows}
            loading={loading}
            onRowClick={(row) => navigate(`/prescriptions/${row.id}`)}
          />
        )}
        <Pagination page={page} pageSize={25} total={count} onPageChange={setPage} />
      </Card>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="New Prescriptions">
        <Input label="Rx number" value={String(form.prescription_number ?? "")} onChange={(e) => setForm({ ...form, prescription_number: e.target.val })} />
        <Textarea label="Notes" rows={3} value={String(form.notes ?? "")} onChange={(e) => setForm({ ...form, notes: e.target.value })} />
        <Select label="Status" value={String(form.status ?? "")} onChange={(e) => setForm({ ...form, status: e.target.value })} options={["draft", "active"]} />
        <div className="modal-actions">
          <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
          <Button onClick={() => void save()}>Save</Button>
        </div>
      </Modal>
    </div>
  );
}
