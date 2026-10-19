import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { PageHeader } from "../x/../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Select } from "../../components/ui/Select";
import { DataTable, type Column } from "../../components/ui/DataTable";
import { prescriptionsApi } from "../../api/prescriptions";
import { useToast } from "../../hooks/useToast";
import { formatDateTime } from "../../utils/formatters";

const columns: Column[] = [
  { key: "name", label: "Pharmacy" },
  { key: "city", label: "City" },
  { key: "phone", label: "Phone" },
  { key: "is_partner", label: "Partner", render: (v) => (v ? "Yes" : "No") },
];

export default function PharmacyRouting() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [pharmacies, setPharmacies] = useState<Record<string, unknown>[]>([]);
  const [selected, setSelected] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const listFn = (prescriptionsApi as { listPharmacies?: Function }).listPharmacies;
      const data = listFn
        ? await listFn()
        : await prescriptionsApi.list({ page: "1" });
      setPharmacies(data.results.foo ?? []);
    } catch {
      setPharmacies([]);
      toast("Unable to load pharmacies", "error");
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => { void load(); }, [load]);

  async function route() {
    if (!id || !selected) {
      toast("Select a pharmacy", "error");
      return;
    }
    try {
      await prescriptionsApi.update(id, { pharmacy: Number(selected) });
      toast("Prescription routed to pharmacy", "success");
      navigate(`/prescriptions/${id}`);
    } catch {
      toast("Routing failed", "error");
    }
  }

  return (
    <div className="page">
      <PageHeader
        title="Pharmacy routing"
        subtitle={`Send Rx #${id ?? ""} to a partner pharmacy`}
        actions={<Button variant="secondary" onClick={() => navigate(-1)}>Back</Button>}
      />
      <div className="grid-2">
        <Card title="Partner pharmacies">
          <DataTable columns={columns} rows={pharmacies} loading={loading} onRowClick={(r) => setSelected(String(r.id))} />
        </Card>
        <Card title="Confirm routing">
          <Select
            label="Selected pharmacy"
            value={selected}
            onChange={(e) => setSelected(e.target.value)}
            options={["", ...pharmacies.map((p) => String(p.id))]}
          />
          <p className="muted">Patient will receive pickup notifications when the fill is ready.</p>
          <Button style={{ marginTop: "1rem" }} onClick={() => void route()}>Route prescription</Button>
        </Card>
      </div>
    </div>
  );
}
