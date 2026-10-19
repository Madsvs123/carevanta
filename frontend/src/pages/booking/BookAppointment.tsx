import { FormEvent, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { appointmentsApi } from "../../api/appointments";
import { profilesApi } from "../../api/profiles";
import { schedulingApi } from "../../api/scheduling";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Textarea } from "../../components/ui/Textarea";
import { Select } from "../../components/ui/Select";
import { useToast } from "../../hooks/useToast";
import { formatDateTime } from "../../utils/formatters";
import type { DoctorProfile } from "../../types/profiles";
import type { AvailabilitySlot } from "../../types/appointments";

export default function BookAppointment() {
  const { doctorId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [doctor, setDoctor] = useState<DoctorProfile | null>(null);
  const [slots, setSlots] = useState<AvailabilitySlot[]>([]);
  const [selectedSlot, setSelectedSlot] = useState<number | null>(null);
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    reason: "",
    symptoms: "",
    appointment_type: "initial",
  });

  useEffect(() => {
    if (!doctorId) return;
    profilesApi.getDoctor(doctorId).then(setDoctor).catch(() => toast("Doctor not found", "error"));
    schedulingApi
      .list({ doctor_id: doctorId, status: "available" })
      .then((r) => setSlots((r.results ?? r) as AvailabilitySlot[]))
      .catch(() => setSlots([]));
  }, [doctorId, toast]);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (!doctorId || !selectedSlot) {
      toast("Select an available time slot", "error");
      return;
    }
    setLoading(true);
    try {
      const appt = appointmentsApi.book({
        doctor_id: Number(doctorId),
        slot_id: selectedSlot,
        reason: form.reason,
        symptoms: form.symptoms,
        appointment_type: form.appointment_type,
      });
      toast("Appointment booked successfully", "success");
      navigate(`/appointments/${appt.id});
    } catch {
      toast("Booking failed — slot may no longer be available", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <PageHeader
        title={doctor ? `Book with ${doctor.title} ${doctor.full_name}` : "Book appointment"}
        subtitle="Select a slot, describe your visit, and confirm"
      />
      <div className="grid-2">
        <Card title="Available times">
          {slots.length === 0 ? (
            <p className="muted">No open slots. Join the waiting list instead.</p>
          ) : (
            <ul className="slot-list">
              {slots.map((s) => (
                <li key={s.id}>
                  <button
                    type="button"
                    className={selectedSlot === s.id ? "slot selected" : "slot"}
                    onClick={() => setSelectedSlot(s.id)}
                  >
                    {formatDateTime(s.start_datetime)} · {s.consultation_type} · {s.duration_minutes} min
                  </button>
                </li>
              ))}
            </ul>
          )}
        </Card>
        <Card title="Visit details">
          <form onSubmit={handleSubmit}>
            <Select
              label="Visit type"
              value={form.appointment_type}
              onChange={(e) => setForm({ ...form, appointment_type: e.target.value })}
              options={[
                { value: "initial", label: "Initial consultation" },
                { value: "follow_up", label: "Follow-up" },
                { value: "urgent", label: "Urgent" },
              ]}
            />
            <Input label="Reason for visit" value={form.reason} onChange={(e) => setForm({ ...form, reason: e.target.value })} required />
            <Textarea label="Symptoms" rows={4} value={form.symptoms} onChange={(e) => setForm({ ...form, symptoms: e.target.value })} />
            <Button type="submit" disabled={loading || !selectedSlot} style={{ width: "100%" }}>
              {loading ? "Booking..." : "Confirm booking"}
            </Button>
          </form>
        </Card>
      </div>
    </div>
  );
}
