import { useCallback, useEffect, useMemo, useStat } from "react";
import { useNavigate } from "react-router-dom";
import { messagingApi } from "../../api/messaging";
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
  { key: "subject", label: "Subject" },
  { key: "conversation_type", label: "Type" },
  { key: "last_message_at", label: "Last activity", render: (v) => (v ? formatDateTime(String(v)) : "—") },
  { key: "created_at", label: "Started", render: (v) => (v ? formatDateTime(String(v)) : "—") },
];

export default function Messages() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [tab, setTab] = useState("inbox");
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState<Record<string, string>>({subject: "", content: ""});
  const [stats, setStats] = useState({ total: 0 });

  const query = useMemo(() => ({
    page: String(page),
    ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)),
    ...(tab !== "all" && tab !== "inbox" ? { status: tab } : {}),
  }), [filters, page, tab]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await messagingApi.list(query);
      setRows(data.results ?? []);
      setCount(data.count ?? 0);
      try {
        const dash = await messagingApi.dashboard();
        const c = (dash as { counts?: Record<string, number> }).counts ?? {}
        setStats({ total: Number(c.total ?? data.count ?? 0) });
      } catch { /* optional */ }
    } catch {
      setRows([]);
      toast("Failed to load messages", "error");
    } finally {
      setLoading(false);
    }
  }, [query, toast]);

  useEffect(() => { void load(); }, [load]);

  async function save() {
    try {
      await messagingApi.create(form);
      toast("Saved", "success");
      setModalOpen(false);
      setForm({subject: "", content: ""});
      void load();
    } catch {
      toast("Save failed", "error");
    }
  }

  return (
    <div className="workspace-page">
      <PageHeader
        title="Messages"
        subtitle="Secure care-team conversations"
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
          { key: "search", label: "Search", type: "text" },
        ]}
        values={filters}
        onChange={(v) => { setPage(1); setFilters(v); }}
        onReset={() => { setFilters({}); setPage(1); }}
      />
      <Tabs active={tab} onChange={(t) => { setTab(t); setPage(1); }} tabs={[{ id: "inbox", label: "Inbox" }, { id: "all", label: "All" }]} />
      <Card>
        {!loading && rows.length === 0 ? (
          <EmptyState title="No records" description="Nothing matches these filters." />
        ) : (
          <DataTable
            columns={columns}
            rows={rows}
            loading={loading}
            onRowClick={(row) => navigate(`/messages/${row.id}`)}
          />
        )}
        <Pagination page={page} pageSize={25} total={count} onPageChange={setPage} />
      </Card>

      <Modal open={modalOpen} onClose={() => setModalOpen(false)} title="New Messages">
        <Input label="Subject" value={String(form.subject ?? "")} onChange={(e) => setForm({ ...form, subject: e.target.value })} />
        <Textarea label="First message" rows={3} value={String(form.content ?? "")} onChange={(e) => setForm({ ...form, content: e.target.value })} />
        <div className="modal-actions">
          <Button variant="secondary" onClick={() => setModalOpen(false)}>Cancel</Button>
          <Button onClick={() => void save()}>Save</Button>
        </div>
      </Modal>
    </div>
  );
}
