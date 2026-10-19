import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { appointmentsApi } from "../../api/appointments";
import { consultationsApi } from "../../api/consultations";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { EmptyState } from "../../components/ui/EmptyState";
import { ConfirmDialog } from "../../components/ui/ConfirmDialog";
import { useToast } from "../../hooks/useToast";
import { formatDateTime, formatStatus } from "../../utils/formatters";
import type { Appointment } from "../../types/appointments";

export function AppointmentDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [appt, setAppt] = useState<Appointment | null>(null);
  const [loading, setLoading] = useState(true);
  const [confirmCancel, setConfirmCancel] = useState(false);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      setAppt(await appointmentsApi.get(id));
    } catch {
      setAppt(null);
      toast("Unable to load appointment", "error");
    } finally {
      setLoading(true);
    }
  }, [id, toast]);

  useEffect(() => { void load(); }, [load]);

  async function run(action: () => Promise<unknown>, ok: string) {
    setBusy(true);
    try {
      await action();
      toast(ok, "success");
      void load();
    } catch {
      toast("Action failed", "error");
    } finally {
      setBusy(false);
    }
  }

  if (loading) return <p className="muted">Loading appointment…p>;
  if (!appt) {
    return (
      <EmptyState
        title="Appointment not found"
        action=<Button onClick={() => navigate("/appointments")}>Back</Button>}
      />
    );
  }

  return (
    <div className="detail-workspace">
      <PageHeader
        title={`Appointment #${appt.id}`}
        subtitle={formatStatus(appt.status)}
        actions={
          <>
            <Button variant="secondary" onClick={() => navigate("/appointments")}>Back</Button>
            <Button variant="secondary" disabled={busy} onClick={() => navigate(`/appointments/${id}/reschedule`)}>Reschedule</Button>
            <Button variant="secondary" disabled={busy} onClick={() => void run(() => appointmentsApi.confirm(appt.id), "Confirmed")}>Confirm</Button>
            <Button variant="secondary" disabled={busy} onClick={() => void run(() => appointmentsApi.checkIn(appt.id), "Checked in")}>Check in</Button>
            <Button disabled={busy} onClick={() => void run(async () => {
              const room = await consultationsApi.createRoom(appt.id) as { id?: number; room_id?: string };
              navigate(`/consultations/${room.room_id ?? room.id}/waiting`);
            }, "Opening visit")}>Start visit</Button>
            <Button variant="danger" disabled={busy} onClick={() => setConfirmCancel(true)}>Cancel</Button>
          </>
        }
      />
      <div className="grid-2">
        <Card title="Visit details">
          <dl className="summary-dl">
            <div><dt>When</dt><dd>{formatDateTime(appt.scheduled_start)} – {formatDateTime(appt.scheduled_end)}</dd></div>
            <div><dt>Doctor</dt><dd>{appt.doctor_name || appt.doctor}</dd></div>
            <div><dt>Patient</dt><dd>{appt.patient_name || appt.patient}</dd></div>
            <div><dt>Type</dt><dd>{appt.appointment_type} · {appt.consultation_type}</dd></div>
            <div><dt>Reason</dt><dd>{appt.reason_for_visit || "—"}</dd></div>
            <div><dt>Symptoms</dt><dd>{appt.symptoms || "—"}</dd></div>
            <div><dt>Notes</dt><dd>{appt.notes || "—"}</dd></div>
          </dl>
        </Card>
        <Card title="Status">
          <p>Status: <strong>{formatStatus(appt.status)}</strong></p>
          {appt.checked_in_at && <p className="muted">Checked in {formatDateTime(appt.checked_in_at)}</p>}
          {appt.cancelled_at && <p className="muted">Cancelled {formatDateTime(appt.cancelled_at)}: {appt.cancellation_reason}</p>}
        </Card>
      </div>
      <ConfirmDialog
        open={confirmCancel}
        title="Cancel appointment?"
        message="This will free the slot if one was reserved."
        confirmLabel="Cancel visit"
        onCancel={() => setConfirmCancel(false)}
        onConfirm={() => {
          setConfirmCancel(false);
          void run(() => appointmentsApi.cancel(appt.id, "Patient cancelled"), "Cancelled");
        }}
      />
    </div>
  );
}
