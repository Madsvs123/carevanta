import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { medicalRecordsApi } from "../../api/medicalRecords";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Tabs } from "../../components/ui/Tabs";
import { EmptyState } from "../../components/ui/EmptyState";
import { useToast } from "../../hooks/useToast";
import { formatDateTime } from "../../utils/formatters";

export default function RecordDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [record, setRecord] = useState<Record<string, unknown> | null>(null);
  const [tab, setTab] = useState("overview");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      setRecord(await medicalRecordsApi.get(id));
    } catch {
      setRecord(null);
      toast("Unable to load record", "error");
    } finally {
      setLoading(false);
    }
  }, [id, toast]);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) return <p className="muted">Loading…</p>;
  if (!record) {
    return (
      <EmptyState
        title="Record not found"
        action={<Button onClick={() => navigate("/medical-records")}>Back</Button>}
      >
    );
  }

  return (
    <div className="detail-workspace">
      <PageHeader
        title={String(record.title ?? `Record #${id}`)}
        subtitle={String(record.diagnosis ?? record.chief_complaint ?? "")}
        actions={
          <>
            <Button variant="secondary" onClick={() => navigate("/medical-records")}>
              Back
            </Button>
            <Button
              variant="secondary"
              onClick={() =>
                medicalRecordsApi
                  .archive(String(id))
                  .then(() => {
                    toast("Archived", "success");
                    void load();
                  })
                  .catch(() => toast("Archive failed", "error"))
              }
            >
              Archive
            </Button>
          </>
        }
      />
      <Tabs
        active={tab}
        onChange={setTab}
        tabs={[
          { id: "overview", label: "Overview" },
          { id: "plan", label: "Plan" },
        ]}
      />
      {tab === "overview" && (
        <div className="grid-2">
          <Card title="Clinical">
            <dl className="summary-dl">
              <div>
                <dt>Chief complaint</dt>
                <dd>{String(record.chief_complaint ?? "—")}</dd>
              </div>
              <div>
                <dt>Diagnosis</dt>
                <dd>{String(record.diagnosis ?? "—")}</dd>
              </div>
              <div>
                <dt>Created</dt>
                <dd>{formatDateTime(String(record.created_at ?? ""))}</dd>
              </div>
            </dl>
          </Card>
          <Card title="Symptoms">
            <p>{JSON.stringify(record.symptoms ?? [])}</p>
          </Card>
        </div>
      )}
      {tab === "plan" && (
        <Card title="Treatment plan">
          <p>{String(record.treatment_plan ?? "—")}</p>
          <p className="muted">{String(record.follow_up_instructions ?? "")}</p>
        </Card>
      )}
    </div>
  );
}
