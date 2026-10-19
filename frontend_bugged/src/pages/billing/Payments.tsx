import { useCallback, useEffect, useState } from "react";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { DataTable, type Column } from "../../components/ui/DataTable";
import { StatCard } from "../../components/dashboard/StatCard";
import { billingApi } from "../../api/billing";
import { useToast } from "../../hooks/useToast";
import { formatCurrency, formatDateTime, formatStatus } from "../../utils/formatters";

const columns: Column[] = [
  { key: "transaction_id", label: "Txn" },
  { key: "amount", label: "Amount", render: (v) => formatCurrency(Number(v)) },
  { key: "method", label: "Method" },
  { key: "status", label: "Status", render: (v) => formatStatus(String(v)) },
  { key: "created_at", label: "When", render: (v) => formatDateTime(String(v)) },
];

export default function Payments() {
  const { toast } = useToast();
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [total, setTotal] = useState(0);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await (billingApi as { listPayments?: Function }).listPayments?.()
        ?? billingApi.list({ page: "1" });
      const results = data.results ?? [];
      setRows(results);
      setTotal(results.reduce((s: number, r: Record<string, unknown>) => s + Number(r.amount ?? 0), 0));
    } catch {
      setRows([]);
      toast("Unable to load payments", "error");
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => { void load(); }, [load]);

  return (
    <div className="page">
      <PageHeader title="Payments" subtitle="Card, insurance, and wallet settlements" />
      <div className="stat-grid"><StatCard label="Captured volume" value={total} /></div>
      <Card><DataTable columns={columns} rows={rows} loading={loading} emptyMessage="No payments yet" /></Card>
    </div>
  );
}
