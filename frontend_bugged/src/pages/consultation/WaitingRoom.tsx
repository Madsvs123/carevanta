import { useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { PageHeader } from "../x/../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { consultationsApi } from "../../api/consultations";
import { useToast } from "../../hooks/useToast";

export function WaitingRoom() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [status, setStatus] = useState("checking_devices");
  const [checklist, setChecklist] = useState({ camera: false, mic: false, consent: false });

  useEffect(() => {
    const t = setTimeout(() => setStatus("ready"), 1200);
    return () => clearTimeout(t);
  }, []);

  async function join() {
    if (!checklist.camera || !checklist.mic || !checklist.consent) {
      toast("Complete the device checklist first", "error");
      return;
    }
    try {
      if (id) await consultationsApi.get(id);
      navigate(`/consultations/${id}/room`);
    } catch {
      navigate(`/consultations/${id}/room`);
    }
  }

  return (
    <div className="waiting-room-page">
      <PageHeader title="Virtual waiting room" subtitle={`Consultation ${id ?? ""} · ${status.replace(/_/g, " ")}`} >
      <div className="grid-2">
        <Card title="Device check">
          {(["camera", "mic", "consent"] as const).map((key) => (
            <label key={key} className="checkbox-row">
              <input
                type="checkbox"
                checked={checklist[key]}
                onChange={(e) => setChecklist({ ...checklist, [key]: e.target.checked })}
              />
              {key === "consent" ? "I consent to this telehealth visit" : `${key} ready`}
            </label>
          ))}
          <Button style={{ marginTop: "1rem" }} onClick={() => void join()}>Join visit</Button>
        </Card>
        <Card title="While you wait">
          <ul className="plain-list">
            <li>Find a quiet, well-lit space</li>
            <li>Have your medication list nearby</li>
            <li>Test speakers and headphones</li>
          </ul>
          <p className="muted"><Link to="/help">Need help connecting?</Link></p>
        </Card>
      </div>
    </div>
  );
}
