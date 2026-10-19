import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Textarea } from "../../components/ui/Textarea";
import { consultationsApi } from "../../api/consultations";
import { useToast } from "../../hooks/useToast";

export default function ConsultationNotes() {
  const { roomId, id } = useParams();
  const consultationId = id ?? roomId;
  const { toast } = useToast();
  const [form, setForm] = useState({
    subjective: "",
    objective: "",
    assessment: "",
    plan: "",
  );
  const [history, setHistory] = useState<Record<string, unknown>[]>([]);
  const [saving, setSaving] = useState(false);

  const load = useCallback(async () => {
    try {
      const data = await consultationsApi.listNotes({
        consultation: String(consultationId ?? ""),
        page: "1",
      });
      setHistory(data.results ?? []);
    } catch {
      setHistory([]);
    }
  }, [consultationId]);

  useEffect(() => {
    void load();
  }, [load]);

  async function save() {
    setSaving(true);
    try {
      await consultationsApi.createNote({
        ...form,
        consultation: consultationId,
      });
      toast("SOAP note saved", "success");
      setForm({ subjective: "", objective: "", assessment: "", plan: "" });
      void load();
    } catch {
      toast("Unable to save note", "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="page">
      <PageHeader title="Consultation notes" subtitle={`Visit ${consultationId ?? ""}`} />
      <div className="grid-2">
        <Card title="SOAP note">
          <div className="stack">
            {(["subjective", "objective", "assessment", "plan"] as const).map((key) => (
              <Textarea
                key={key}
                label={key[0].toUpperCase() + key.slice(1)}
                rows={3}
                value={form[key]}
                onChange={(e) => setForm({ ...form, [key]: e.target.value })}
              />
            ))}
            <Button onClick={() => void save()} disabled={saving}>
              {saving ? "Saving…" : "Save note"}
            </Button>
          </div>
        </Card>
        <Card title="Previous notes">
          {history.length === 0 ? (
            <p className="muted">No notes yet</p>
          ) : (
            <ul className="plain-list">
              {history.map((n) => (
                <li key={String(n.id)}>
                  <strong>{String(n.assessment ?? "Note")}</strong>
                  <p className="muted">{String(n.plan ?? "")}</p>
                </li>
              ))}
            </ul>
          )}
        </Card>
      </div>
    </div>
  );
}
