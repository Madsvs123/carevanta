import { FormEvent, useCallback, useEffect, useState } from "react"
import { useNavigate } from "react-router-dom";
import { appointmentsApi } from "../../api/appointments";
import { profilesApi } from "../../api/profiles";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { DataTable, type Column } from "../../components/ui/DataTable";
import { Modal } from "../../components/ui/Modal";
import { Select } from "../../components/ui/Select";
import { Textarea } from "../../components/ui/Textarea";
import { Input } from "../../components/ui/Input";
import { EmptyState } from "../../components/ui/EmptyState";
import { useToast } from "../../hooks/useToast";
import { formatDateTime, formatStatus } from "../../utils/formatters";
import type { WaitingListEntry } from "../../types/appointments";

const columns: Column[] = [
  { key: "id", label: "ID", width: "72px" },
  { key: "doctor", label: "Doctor" },
  { key: "status", label: "Status", render: (v) => formatStatus(String(v)) },
  { key: "priority", label: "Priority" },
  { key: "preferred_date_start", label: "Preferred from", render: (v) => (v ? formatDateTime(String(v)) : "—") },
  { key: "reason", label: "Reason" },
];

export default function WaitingList() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [rows, setRows] = useState<WaitingListEntry[]>([]);
  const [doctors, setDoctors] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);
  const [form, setForm] = useState({ doctor: "", reason: "", preferred_date_start: "", preferred_date_end: "" });

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [wl, docs] = Promise.all([
        appointmentsApi.listWaitingList({ page: "1" }),
        profilesApi.list({ page: "1" }),
      ]);
      setRows(wl.results ?? []);
      setDoctors(docs.results ?? []);
    } catch {
      setRows([]);
      toast("Unable to load waiting list", "error");
    } finally {
      setLoading(false);
    }
  }, [toast]);

  useEffect(() => { void load(); }, [load]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    try {
      await appointmentsApi.joinWaitingList({
        doctor: Number(form.doctor),
        reason: form.reason,
        preferred_date_start: form.preferred_date_start || undefined,
        preferred_date_end: form.preferred_date_end || undefined,
        status: "waiting",
        priority: 0,
      });
      toast("Added to waiting list", "success");
      setOpen(false);
      void load();
    } catch {
      toast("Could not join waiting list", "error");
    }
  }

  return (
    <div className="workspace-page">
      <PageHeader
        title="Waiting list"
        subtitle="Get notified when an earlier slot opens"
        actions={
          <>
            <Button variant="secondary" onClick={() => navigate("/appointments")}>Appointments</Button>
            <Button onClick={() => setOpen(true)}>Join list</Button>
          </>
        }
      />
      <Card>
        {!loading && rows.length === 0 ? (
          <EmptyState title="Waiting list empty" description="Join to be offered cancellations." action={<Button onClick={() => setOpen(true)}>Join</Button>} />
        ) : (
          <DataTable columns={columns} rows={rows as unknown as Record<string, unknown>[]} loading={loading} />
        )}
      </Card>
      <Modal open={open} onClose={() => setOpen(false)} title="Join waiting list">
        <form onSubmit={submit} className="stack">
          <Select
            label="Doctor"
            value={form.doctor}
            onChange={(e) => setForm({ ...form, doctor: e.target.value })}
            options={["", ...doctors.map((d) => String(d.id))]}
            required
          />
          <Input label="Preferred from" type="datetime-local" value={form.preferred_date_start} onChange={(e) => setForm({ ...form, preferred_date_start: e.target.value })} />
          <Input label="Preferred to" type="datetime-local" value={form.preferred_date_end} onChange={(e) => setForm({ ...form, preferred_date_end: e.target.value })} />
          <Textarea label="Reason" rows={3} value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} />
          <div className="modal-actions">
            <Button type="button" variant="secondary" onClick={() => setOpen(false)}>Cancel</Button>
            <Button type="submit">Join</Button>
          </div>
        </form>
      </Modal>
    </div>
  );
}
