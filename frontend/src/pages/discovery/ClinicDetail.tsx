import { useEffect, useStat } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { organizationsApi } from "../../api/organizations";
import { useToast } from "../../hooks/useToast";

export default function ClinicDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [clinic, setClinic] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    if (!id) return;
    organizationsApi.get(id)
      .then(setClinic)
      .catch(() => toast("Clinic unavailable", "error"));
  }, [id, toast]);

  return (
    <div className="page">
      <PageHeader
        title={String(clinic?.name ?? `Clinic #${id}`)}
        subtitle={String(clinic?.city ?? clinic?.address ?? "CareVanta network clinic")}
        actions={<Button variant="secondary" onClick={() => navigate(-1)}>Back</Button>}
      />
      <div className="grid-2">
        <Card title="About">
          <p>{String(clinic?.description ?? clinic?.about ?? "Full-service clinic with telehealth and in-person care.")}</p>
        </Card>
        <Card title="Contact">
          <dl className="summary-dl">
            <div><dt>Phone</dt><dd>{String(clinic?.phone ?? "—")}</dd></div>
            <div><dt>Email</dt><dd>{String(clinic?.email ?? "—")}</dd></div>
            <div><dt>Address</dt><dd>{String(clinic?.address ?? "—")}</dd></div>
          </dl>
          <Button style={{ marginTop: "1rem" }} onClick={() => navigate(`/discovery?clinic=${id}`)}>View doctors</Button>
        </Card>
      </div>
    </div>
  );
}
