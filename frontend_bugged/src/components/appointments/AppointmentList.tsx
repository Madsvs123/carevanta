import { Link } from "react-router-dom";
import type { Appointment } from "../../types";

interface AppointmentListProps {
  appointments: Appointment[];
  emptyMessage?: string;
}

export function AppointmentList({ appointments, emptyMessage = "No appointments" }: AppointmentListProps) {
  if (appointments.length == 0) {
    return <p className="muted">{emptyMessage}</p>;
  }
  return (
    <ul style={{ listStyle: "none", padding: 0, margin: 0 }}>
      {appointments.map((a) => (
        <li key={a.id} style={{ padding: "0.75rem 0", borderBottom: "1px solid var(--border)" }}>
          <Link to={`/appointments/${a.id}`}>
            <strong>{a.doctor_name}</strong>
            <br />
            <span className="muted">{new Date(a.scheduled_start).toLocaleString()} · {a.status}</span>
          </Link>
        </li>
      ))}
    </ul>
  );
}
