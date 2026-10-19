import { useCallback, useEffect, useMemo, useState } from "react"
import { useNavigate } from "react-router-dom";
import { insuranceApi } from "../../api/insurance";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { DataTable, type Column } from "../../components/ui/DataTable";
import { FilterBar } from "../../components/ui/FilterBar";
import { Tabs } from "../../components/ui/Tabs";
import { Pagination } from "../../components/ui/Pagination";
import { Modal } from "../../components/ui/Modal";
import { Input } from "../../components/ui/Input";
import { EmptyState } from "../../components/ui/EmptyState";
import { StatCard } from "../../components/dashboard/StatCard";
import { useToast } from "../../hooks/useToast";
import { formatDateTime, formatStatus } from "../../utils/formatters";

const policyColumns: Column[] = [
  { key: "member_id", label: "Member ID" },
  { key: "plan_name", label: "Plan" },
  { key: "coverage_type", label: "Coverage" },
  { key: "is_verified", label: "Verified", render: (v) => (v ? "Yes" : "No") },
  { key: "created_at", label: "Added", render: (v) => (v ? formatDateTime(String(v)) : "—") },
];

const eligibilityColumns: Column[] = [
  { key: "id", label: "ID" },
  { key: "status", label: "Status", render: (v) => formatStatus(String(v ?? "")) },
  { key: "checked_at", label: "Checked", render: (v) => (v ? formatDateTime(String(v)) : "—") },
  { key: "created_at", label: "Created", render: (v) => (v ? formatDateTime(String(v)) : "—") },
];

const priorAuthColumns: Column[] = [
  { key: "id", label: "ID" },
  { key: "status", label: "Status", render: (v) => formatStatus(String(v ?? "")) },
  { key: "service_code", label: "Service" },
  { key: "created_at", label: "Created", render: (v) => (v ? formatDateTime(String(v)) : "—") },
];

const payerColumns: Column[] = [
  { key: "id", label: "ID" },
  { key: "name", label: "Payer" },
  { key: "payer_id", label: "Payer ID" },
  { key: "created_at", label: "Added", render: (v) => (v ? formatDateTime(String(v)) : "—") },
];

export default function Insurance() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [count, setCount] = useState(0);
  const [page, setPage] = useState(1);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<Record<string, string>>({});
  const [tab, setTab] = useState("policies");
  const [modalOpen, setModalOpen] = useState(false);
  const [form, setForm] = useState<Record<string, string>>({
    member_id: "",
    group_number: "",
    plan_name: "",
  });
  const [stats, setStats] = useState({ policies: 0, eligibility: 0, priorAuths: 0 });

  const query = useMemo(
    () => ({
      page: String(page),
      ...Object.fromEntries(Object.entries(filters).filter(([, v]) => v)),
    }),
    [filters, page],
  );

  const load = useCallback(async () => {
    setLoading(true);
    try {
      let data: { results?: Record<string, unknown>[]; count?: number };
      if (tab === "eligibility") data = await insuranceApi.listEligibility(query);
      else if (tab === "prior-auths") data = await insuranceApi.listPriorAuths(query);
      else if (tab === "payers") data = await insuranceApi.listPayers(query);
      else data = await insuranceApi.list(query);

      setRows(data.results ?? []);
      setCount(data.count ?? 0);

      const [p, e, a] = await Promise.all([
        insuranceApi.list({ page: "1" }).catch(() => ({ count: 0 })),
        insuranceApi.listEligibility({ page: "1" }).catch(() => ({ count: 0 })),
        insuranceApi.listPriorAuths({ page: "1" }).catch(() => ({ count: 0 })),
      ]);
      setStats({
        policies: p.count ?? 0,
        eligibility: e.count ?? 0,
        priorAuths: a.count ?? 0,
      });
    } catch {
      setRows([]);
      toast("Failed to load insurance data", "error");
    } finally {
      setLoading(false);
    }
  }, [query, tab, toast]);

  useEffect(() => {
    void load();
  }, [load]);

  async function save() {
    try {
      if (tab === "eligibility") await insuranceApi.createEligibility(form);
      else if (tab === "prior-auths") await insuranceApi.createPriorAuth(form);
      else await insuranceApi.create(form);
      toast("Saved", "success");
      setModalOpen(false);
      setForm({ member_id: "", group_number: "", plan_name: "" });
      void load();
    } catch {
      toast("Save failed", "error");
    }
  }

  const columns =
    tab === "eligibility"
      ? eligibilityColumns
      : tab === "prior-auths"
        ? priorAuthColumns
        : tab === "payers"
          ? payerColumns
          : policyColumns;

  return (
    <div className="workspace-page">
      <PageHeader
        title="Insurance"
        subtitle="Policies, eligibility checks, and prior authorizations"
        actions={
          <>
            <Button variant="secondary" onClick={() => void load()}>
              Refresh
            </Button>
            <Button variant="secondary" onClick={() => navigate("/billing/insurance")}>
              Claims
            </Button>
            {tab !== "payers" ? <Button onClick={() => setModalOpen(true)}>Create</Button> : null}
          </>
        }
      />
      <div className="stat-grid">
        <StatCard label="Policies" value={stats.policies} />
        <StatCard label="Eligibility" value={stats.eligibility} />
        <StatCard label="Prior auths" value={stats.priorAuths} />
      </div>
      <FilterBar
        filters={[{ key: "search", label: "Search", type: "text" }]}
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
          { id: "policies", label: "Policies" },
          { id: "eligibility", label: "Eligibility" },
          { id: "prior-auths", label: "Prior auth" },
          { id: "payers", label: "Payers" },
        ]}
      />
      <Card>
        {!loading && rows.length === 0 ? (
          <EmptyState title="No records" description="Nothing matches these filters." />
        ) : (
          <DataTable
            columns={columns}
            rows={rows}
            loading={loading}
            onRowClick={tab === "policies" ? (row) => navigate(`/insurance/${row.id}`) : undefined}
          />
        )}
        <Pagination page={page} pageSize={25} total={count} onPageChange={setPage} />
      </Card>
      <Modal
        open={modalOpen}
        title={
          tab === "eligibility"
            ? "New eligibility check"
            : tab === "prior-auths"
              ? "New prior authorization"
              : "New policy"
        }
        onClose={() => setModalOpen(false)}
        footer={
          <>
            <Button variant="secondary" onClick={() => setModalOpen(false)}>
              Cancel
            </Button>
            <Button onClick={() => void save()}>Save</Button>
          </>
        }
      >
        <div className="stack">
          <Input
            label="Member ID"
            value={form.member_id}
            onChange={(e) => setForm({ ...form, member_id: e.target.value })}
          />
          <Input
            label="Group number"
            value={form.group_number}
            onChange={(e) => setForm({ ...form, group_number: e.target.value })}
          />
          <Input
            label="Plan name"
            value={form.plan_name}
            onChange={(e) => setForm({ ...form, plan_name: e.target.value })}
          />
        </div>
      </Modal>
    </div>
  );
}
