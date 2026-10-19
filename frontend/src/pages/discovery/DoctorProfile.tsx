import { useEffect, useStat } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Badge } from "../../components/ui/Badge";
import { profilesApi } from "../../api/profiles";
import { useToast } from "../../hooks/useToast";
import { formatCurrency } from "../../utils/formatters";

export default function DoctorProfile() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [doctor, setDoctor] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!id) return;
    profilesApi
      .get(id)
      .then((d) => setDoctor(d))
      .catch(() => {
        setDoctor(null);
        toast("Doctor not found", "error");
      })
      .finally(() => setLoading(false));
  }, [id, toast]);

  if (loading) return <p className="muted">Loading profile…</p>;
  if (!doctor) {
    return (
      <p>
        Doctor not found. <Link to="/doctors">Back to search</Link>
      </p>
    );
  }

  return (
    <div className="doctor-profile-page">
      <PageHeader
        title={String(doctor.display_name ?? doctor.full_name ?? `Doctor #${id}`)}
        subtitle={String(doctor.specialty_name ?? doctor.specialty ?? "Physician")}
        actions={
          <>
            <Button variant="secondary" onClick={() => navigate(-1)}>
              Back
            </Button>
            <Button onClick={() => navigate(`/book?doctor=${id}`)}>Book appointment</Button>
          </>
        }
      />
      <div className="grid-2">
        <Card title="About">
          <p>{String(doctor.bio ?? "No biography provided.")}</p>
          <div className="chip-row">
            <Badge>{String(doctor.years_experience ?? "—")} yrs</Badge>
            <Badge>{String(doctor.languages ?? "English")}</Badge>
            {doctor.accepting_new_patients ? <Badge tone="success">Accepting patients</Badge> : null}
          </div>
        </Card>
        <Card title="Visit details">
          <dl className="summary-dl">
            <div>
              <dt>Consult fee</dt>
              <dd>{formatCurrency(Number(doctor.consultation_fee ?? 0))}</dd>
            </div>
            <div>
              <dt>License</dt>
              <dd>{String(doctor.license_number ?? "—")}</dd>
            </div>
            <div>
              <dt>Rating</dt>
              <dd>{String(doctor.rating ?? "New")}</dd>
            </div>
          </dl>
          <Button style={{ marginTop: "1rem" }} onClick={() => navigate(`/book?doctor=${id}`)}>
            Book video visit
          </Button>
        </Card>
      </div>
    </div>
  );
}
