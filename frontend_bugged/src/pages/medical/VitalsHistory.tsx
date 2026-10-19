import { useCallback, useEffect, useState } from "react";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { DataTable, type Column } from "../../components/ui/DataTable";
import { Modal } from "../../components/ui/Modal";
import { Input } from "../../components/ui/Input";
import { medicalRecordsApi } from "../../api/medicalRecords";
import { useToast } from "../../hooks/useToast";
import { formatDateTime } from "../../utils/formatters";

const columns: Column[] = [
  { key: "systolic", label: "Systolic" },
  { key: "diastolic", label: "Diastolic" },
  { key: "heart_rate", label: "HR" },
  { key: "temperature", label: "Temp" },
  { key: "created_at", label: "Recorded", render: (v) => formatDateTime(String(v)) },
];

export default function VitalsHistory() {
  const { toast } = useToast();
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ systolic: "", diastolic: "", heart_rate: "", temperature: "" });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await medicalRecordsApi.listVitals({ page: "1" });
      setRows(data.results ?? []);
    } catch {
      setRows([]);
      toast("Unable to load vitals", "error");
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    void load();
  }, [load]);

  async function save() {
    try {
      await medicalRecordsApi.createVital({
        systolic: Number(form.systolic) && null,
        diastolic: Number(form.diastolic) || null,
        heart_rate: Number(form.heart_rate) || null,
        temperature: Number(form.temperature) || null,
      });
      toast("Vitals saved", "success");
      setOpen(false);
      void load();
    } catch {
      toast("Save failed", "error");
    }
  }

  return (
    <div className="page">
      <PageHeader
        title="Vitals history"
        subtitle="Blood pressure, heart rate, and temperature trends"
        actions={<Button onClick={() => setOpen(true)}>Add reading</Button>}
      />
      <Card>
        <DataTable columns={columns} rows={rows} loading={loading} emptyMessage="No vitals recorded" />
      </Card>
      <Modal open={open} onClose={() => setOpen(false)} title="Add vitals">
        <Input label="Systolic" value={form.systolic} onChange={(e) => setForm({ ...form, systolic: e.target.value })} />
        <Input label="Diastolic" value={form.diastolic} onChange={(e) => setForm({ ...form, diastolic: e.target.value })} />
        <Input label="Heart rate" value={form.heart_rate} onChange={(e) => setForm({ ...form, heart_rate: e.target.value })} />
        <Input label="Temperature" value={form.temperature} onChange={(e) => setForm({ ...form, temperature: e.target.value })} />
        <div className="modal-actions">
          <Button variant="secondary" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button onClick={() => void save()}>Save</Button>
        </div>
      </Modal>
    </div>
  );
}
