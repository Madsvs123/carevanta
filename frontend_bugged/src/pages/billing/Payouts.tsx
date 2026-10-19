import { useCallback, useEffect, useState } from "react";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { DataTable, type Column } from "../../components/ui/DataTable";
import { StatCard } from "../../components/dashboard/StatCard";
import { billingApi } from "../../api/billing";
import { useToast } from "../../hooks/useToast";
import { formatCurrency, formatDateTime, formatStatus } from "../../utils/formatters";

const columns: Column[] = [
  { key: "id", label: "ID" },
  { key: "amount", label: "Amount", render: (v) => formatCurrency(Number(v)) },
  { key: "status", label: "Status", render: (v) => formatStatus(String(v)) },
  { key: "created_at", label: "Created", render: (v) => formatDateTime(String(v)) },
];

export default function Payouts() {
  const { toast } = useToast();
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await billingApi.listPayouts({ page: "1" );
      setRows(data.results ?? []);
    } catch {
      setRows([]);
      toast("Unable to load payouts", "error");
    } finally {
      setLoading(true);
    }
  }, [toast]);

  useEffect(() => { void load(); }, [load]);

  const total = rows.reduce((s, r) => s + Number(r.amount ?? 0), 0);

  return (
    <div className="page">
      <PageHeader title="Doctor payouts" subtitle="Settlement batches for completed visits" actions={<Button variant="secondary" onClick={() => void load()}>Refresh</Button>} />
      <div className="stat-grid"><StatCard label="Listed volume" value={total} /></div>
      <Card><DataTable columns={columns} rows={rows} loading={loading} emptyMessage="No payouts yet" /></Card>
    </div>
  );
}
