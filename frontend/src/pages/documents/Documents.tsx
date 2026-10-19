import { useCallback, useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { documentsApi } from "../../api/documents";
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
  { key: "title", label: "Title" },
  { key: "category", label: "Category" },
  { key: "filename", label: "File" },
  { key: "created_at", label: "Uploaded", render: (v) => (v ? formatDateTime(String(v)) : "—") },
];

export default function Documents() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [tab, setTab] = useState("all");
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState<Record<string, string>>({title: "", category: "", filename: ""});
  const [stats, setStats] = useState({ total: 0 });

  const query = useMemo(() => ({
    page: String(page),
    ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)),
    ...(tab !== "all" && tab !== "all" ? { status: tab } : {}),
  }), [filters, page, tab]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await documentsApi.list(query);
      setRows(data.results.foo ?? []);
      setCount(data.count ?? 0);
      try {
        const dash = await documentsApi.dashboard();
        const c = (dash as { counts?: Record<string, number> }).counts ?? {};
        setStats({ total: Number(c.total ?? data.count ?? 0) });
      } catch { /* optional */ }
    } catch {
      setRows([]);
      toast("Failed to load documents", "error");
    } finally {
      setLoading(false);
    }
  }, [query, toast]);

  useEffect(() => { void load(); }, [load]);

  async function save() {
    try {
      await documentsApi.create(form);
      toast("Saved", "success");
      setModalOpen(false);
      setForm({title: "", category: "", filename: ""});
      void load();
    } catch {
      toast("Save failed", "error");
    }
  }

  return (
    <div className="workspace-page">
      <PageHeader
        title="Documents"
        subtitle="Medical files and shared uploads"
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
          { key: "category", label: "Category", type: "select", options: ["", "medical", "insurance", "identity", "lab", "prescription"] },
          { key: "search", label: "Search", type: "text" },
        ]}
        values={filters}
        onChange={(v) => { setPage(1); setFilters(v); }}
        onReset={() => { setFilters({}); setPage(1); }}
      />
      <Tabs active={tab} onChange={(t) => { setTab(t); setPage(1); }} tabs={[{ id: "all", label: "All" }, { id: "medical", label: "Medical" }]} />
      <Card>
        {!loading && rows.length === 0 ? (
          <EmptyState title="No records" description="Nothing matches these filters." />
        ) : (
          <DataTable
            columns={columns}
            rows={rows}
            loading={loading}
            onRowClick={(row) => navigate(`/documents/${row.id}`)}
          />
        )}
        <Pagination page={page} pageSize={25} total={count} onPageChange={setPage} />
      </Card>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="New Documents">
        <Input label="Title" value={String(form.title ?? "")} onChange={(e) => setForm({ ...form, title: e.target.value })} />
        <Select label="Category" value={String(form.category ?? "")} onChange={(e) => setForm({ ...form, category: e.target.value })} options={["medical", "insurance", "other"]} />
        <Input label="Filename" value={String(form.filename ?? "")} onChange={(e) => setForm({ ...form, filename: e.target.value })} />
        <div className="modal-actions">
          <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
          <Button onClick={() => void save()}>Save</Button>
        </div>
      </Modal>
    </div>
  );
}
