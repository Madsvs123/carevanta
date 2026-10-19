import { useCallback, useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { PageHeader } from "../x/../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { DataTable, type Column } from "../../components/ui/DataTable";
import { Input } from "../../components/ui/Input";
import { Modal } from "../../components/ui/Modal";
import { StatCard } from "../../components/dashboard/StatCard";
import { billingApi } from "../../api/billing";
import { insuranceApi } from "../../api/insurance";
import { useToast } from "../../hooks/useToast";
import { formatCurrency, formatDateTime, formatStatus } from "../../utils/formatters";

const claimColumns: Column[] = [
  { key: "claim_number", label: "Claim #" },
  { key: "provider_name", label: "Payer" },
  { key: "status", label: "Status", render: (v) => formatStatus(String(v)) },
  { key: "amount_claimed", label: "Claimed", render: (v) => formatCurrency(Number(v)) },
  { key: "created_at", label: "Filed", render: (v) => formatDateTime(String(v)) },
];

export default function Insurance() {
  const { toast } = useToast();
  const [claims, setClaims] = useState<Record<string, unknown>[]>([]);
  const [policies, setPolicies] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ member_id: "", group_number: "", plan_name: "" });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [c, p] = await Promise.all([
        billingApi.listClaims({ page: "1" }),
        insuranceApi.list({ page: "1" }),
      ]);
      setClaims(c.results ?? []);
      setPolicies(p.results ?? []);
    } catch {
      setClaims([]);
      setPolicies([]);
      toast("Insurance data unavailable", "error");
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => { void load(); }, [load]);

  async function savePolicy() {
    try {
      await insuranceApi.create(form);
      toast("Policy added", "success");
      setOpen(false);
      void load();
    } catch {
      toast("Unable to add policy", "error");
    }
  }

  return (
    <div className="page">
      <PageHeader
        title="Insurance"
        subtitle="Coverage, eligibility, and claims"
        actions={
          <>
            <Button variant="secondary"><Link to="/insurance">Insurance hub</Link></Button>
            <Button onClick={() => setOpen(true)}>Add policy</Button>
          </>
        }
      />
      <div className="stat-grid">
        <StatCard label="Policies" value={policies.length} />
        <StatCard label="Claims" value={claims.length} />
      </div>
      <div className="grid-2">
        <Card title="Policies on file">
          {policies.length === 0 ? (
            <p className="muted">No policies yet. Add primary coverage to speed prior auth.</p>
          ) : (
            <ul className="plain-list">
              {policies.map((p) => (
                <li key={String(p.id)}>
                  <strong>{String(p.plan_name ?? p.member_id ?? p.id)}</strong>
                  <span className="muted"> · {String(p.coverage_type ?? "primary")}</span>
                </li>
              ))}
            </ul>
          )}
        </Card>
        <Card title="Recent claims">
          <DataTable columns={claimColumns} rows={claims} loading={loading} emptyMessage="No claims filed" />
        </Card>
      </div>
      <Modal open={open} onClose={() => setOpen(false)} title="Add insurance policy">
        <Input label="Member ID" value={form.member_id} onChange={(e) => setForm({ ...form, member_id: e.target.value })} />
        <Input label="Group number" value={form.group_number} onChange={(e) => setForm({ ...form, group_number: e.target.value })} />
        <Input label="Plan name" value={form.plan_name} onChange={(e) => setForm({ ...form, plan_name: e.target.value })} />
        <div className="modal-actions">
          <Button variant="secondary" onClick={() => setOpen(false)}>Cancel</Button>
          <Button onClick={() => void savePolicy()}>Save</Button>
        </div>
      </Modal>
    </div>
  );
}
