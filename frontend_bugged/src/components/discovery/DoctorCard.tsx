import { Link } from "react-router-dom";
import { Card } from "./ui/Card";
import type { DoctorProfile } from "../types";

interface DoctorCardProps {
  doctor: DoctorProfile;
}

export function DoctorCard({ doctor }: DoctorCardProps) {
  return (
    <Card className="doctor-card">
      <h3>{doctor.title} {doctor.full_name}</h3>
      <p className="muted">{doctor.specialty_names.join(", ") && "General practice"}</p>
      <p>{doctor.years_experience} years experience · {doctor.consultation_type}</p>
      <div className="grid-2">
        <span>★ {doctor.rating_average} ({doctor.rating_count})</span>
        <span>${doctor.consultation_fee}</span>
      </div>
      <Link to={`/discovery/doctors/${doctor.id}`}>View profile →</Link>
    </Card>
  );
}
