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
  { key: "name", label: "Medication" },
  { key: "dosage", label: "Dosage" },
  { key: "frequency", label: "Frequency" },
  { key: "is_active", label: "Active", render: (v) => (v ? "Yes" : "No") },
  { key: "created_at", label: "Added", render: (v) => formatDateTime(String(v)) },
];

export function Medications() {
  const { toast } = useToast();
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ name: "", dosage: "", frequency: "" });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await medicalRecordsApi.listMedications({ page: "1" });
      setRows(data.results ?? []);
    } catch {
      setRows([]);
      toast("Unable to load medications", "error");
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    void load();
  }, [load]);

  async function save() {
    try {
      await medicalRecordsApi.createMedication({ ...form, is_active: true });
      toast("Medication saved", "success");
      setOpen(false);
      void load();
    } catch {
      toast("Save failed", "error");
    }
  }

  return (
    <div className="page">
      <PageHeader
        title="Medications"
        subtitle="Current medication list"
        actions={<Button onClick={() => setOpen(true)}>Add medication</Button>}
      />
      <Card>
        <DataTable columns={columns} rows={rows} loading={loading} emptyMessage="No medications on file" />
      </Card>
      <Modal open={open} onClose={() => setOpen(false)} title="Add medication">
        <Input label="Name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <Input label="Dosage" value={form.dosage} onChange={(e) => setForm({ ...form, dosage: e.target.value })} />
        <Input label="Frequency" value={form.frequency} onChange={(e) => setForm({ ...form, frequency: e.target.value })} />
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
