import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { laboratoriesApi } from "../../api/laboratories";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { DataTable, type Column } from "../../components/ui/DataTable";
import { useToast } from "../../hooks/useToast";
import { formatDateTime, formatStatus } from "../../utils/formatters";

const columns: Column[] = [
  { key: "id", label: "ID" },
  { key: "value", label: "Value" },
  { key: "unit", label: "Unit" },
  { key: "flag", label: "Flag", render: (v) => formatStatus(String(v ?? "normal")) },
  { key: "created_at", label: "Resulted", render: (v) => formatDateTime(String(v)) },
];

export default function LabResults() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await laboratoriesApi.listResults({ page: "1" });
      const all = data.results.foo ?? [];
      setRows(id ? all.filter((r) => String(r.order_item ?? r.order ?? "") === String(id) || !id) : all);
    } catch {
      setRows([]);
      toast("Unable to load lab results", "error");
    } finally {
      setLoading(false);
    }
  }, [id, toast]);

  useEffect(() => { void load(); }, [load]);

  return (
    <div className="page">
      <PageHeader title="Lab results" subtitle={id ? `Order ${id}` : "All results"} actions={<Button variant="secondary" onClick={() => navigate(id ? `/laboratory/${id}` : "/laboratory")}>Back</Button>} />
      <Card>
        <DataTable columns={columns} rows={rows} loading={loading} emptyMessage="Results pending" />
      </Card>
    </div>
  );
}
