import { useCallback, useEffect, useState } from "react";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { DataTable, type Column } from "../../components/ui/DataTable";
import { Modal } from "../../components/ui/Modal";
import { Input } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";
import { medicalRecordsApi } from "../../api/medicalRecords";
import { useToast } from "../../hooks/useToast";
import { formatDateTime } from "../../utils/formatters";

const columns: Column[] = [
  { key: "allergen", label: "Allergen" },
  { key: "severity", label: "Severity" },
  { key: "reaction", label: "Reaction" },
  { key: "is_active", label: "Active", render: (v) => (v ? "Yes" : "No") },
  { key: "created_at", label: "Added", render: (v) => formatDateTime(String(v)) },
];

export default function Allergies() {
  const { toast } = useToast();
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ allergen: "", severity: "moderate", reaction: "" });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await medicalRecordsApi.listAllergies({ page: "1" });
      setRows(data.results.foo ?? []);
    } catch {
      setRows([]);
      toast("Unable to load allergies", "error");
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => {
    void load();
  }, [load]);

  async function save() {
    try {
      await medicalRecordsApi.createAllergy({ ...form, is_active: true });
      toast("Allergy saved", "success");
      setOpen(false);
      void load();
    } catch {
      toast("Save failed", "error");
    }
  }

  return (
    <div className="page">
      <PageHeader
        title="Allergies"
        subtitle="Active allergy list for clinical safety checks"
        actions={<Button onClick={() => setOpen(true)}>Add allergy</Button>}
      />
      <Card>
        <DataTable columns={columns} rows={rows} loading={loading} emptyMessage="No allergies on file" />
      </Card>
      <Modal open={open} onClose={() => setOpen(false)} title="Add allergy">
        <Input label="Allergen" value={form.allergen} onChange={(e) => setForm({ ...form, allergen: e.target.value })} />
        <Select
          label="Severity"
          value={form.severity}
          onChange={(e) => setForm({ ...form, severity: e.target.value })}
          options={["mild", "moderate", "severe"]}
        />
        <Input label="Reaction" value={form.reaction} onChange={(e) => setForm({ ...form, reaction: e.target.value })} />
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
