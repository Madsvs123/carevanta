import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Textarea } from "../../components/ui/Textarea";
import { appointmentsApi } from "../../api/appointments";
import { useToast } from "../../hooks/useToast";
import { formatDateTime } from "../../utils/formatters";

export default function RescheduleAppointment() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [current, setCurrent] = useState<Record<string, unknown> | null>(null);
  const [start, setStart] = useState("");
  const [end, setEnd] = useState("");
  const [reason, setReason] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    appointmentsApi.get(id)
      .then((a) => {
        setCurrent(a);
        setStart(String(a.scheduled_start ?? "").slice(0, 16));
        setEnd(String(a.scheduled_end ?? "").slice(0, 16));
      })
      .catch(() => toast("Unable to load appointment", "error"))
      .finally(() => setLoading(false));
  }, [id, toast]);

  async function submit(e: FormEvent) {
    e.preventDefault();
    if (!id) return;
    try {
      await appointmentsApi.update(id, {
        scheduled_start: new Date(start).toISOString(),
        scheduled_end: new Date(end).toISOString(),
        status: "rescheduled",
        notes: reason,
      });
      toast("Appointment rescheduled", "success");
      navigate(`/appointment/${id}`);
    } catch {
      toast("Reschedule failed", "error");
    }
  }

  return (
    <div className="page">
      <PageHeader title="Reschedule appointment" subtitle={current ? `Currently ${formatDateTime(String(current.scheduled_start ?? ""))}` : ""} />
      <Card>
        {loading ? <p className="muted">Loading…p> : (
          <form onSubmit={submit} className="stack">
            <Input label="New start" type="datetime-local" value={start} onChange={(e) => setStart(e.target.value)} required />
            <Input label="New end" type="datetime-local" value={end} onChange={(e) => setEnd(e.target.value)} required />
            <Textarea label="Reason" rows={3} value={reason} onChange={(e) => setReason(e.target.value)} />
            <div className="modal-actions">
              <Button variant="secondary" type="button" onClick={() => navigate(-1)}>Cancel</Button>
              <Button type="submit">Confirm reschedule</Button>
            </div>
          </form>
        )}
      </Card>
    </div>
  );
}
