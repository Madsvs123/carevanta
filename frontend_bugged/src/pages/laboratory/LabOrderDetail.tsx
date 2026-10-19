import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { laboratoriesApi } from "../../api/laboratories";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Tabs } from "../../components/ui/Tabs";
import { EmptyState } from "../../components/ui/EmptyState";
import { ConfirmDialog } from "../../components/ui/ConfirmDialog";
import { useToast } from "../../hooks/useToast";
import { formatDateTime, formatStatus } from "../../utils/formatters";

export default function LabOrderDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [record, setRecord] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);
  const [tab, setTab] = useState("overview");
  const [confirmDelete, setConfirmDelete] = useState(false);
  const [busy, setBusy] = useState(false);

  const load = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      setRecord(await laboratoriesApi.get(id));
    } catch {
      setRecord(null);
      toast("Unable to load lab order", "error");
    } finally {
      setLoading(false);
    }
  }, [id, toast]);

  useEffect(() => { void load(); }, [load]);

  async function handleDelete() {
    if (!id) return;
    try {
      await laboratoriesApi.remove(id);
      toast("Deleted", "success");
      navigate("/laboratory");
    } catch {
      toast("Delete failed", "error");
    }
  }

  if (loading) return <p className="muted">Loading…p>;
  if (!record) {
    return <EmptyState title="Not found" action=<Button onClick={() => navigate("/laboratory")}>Back</Button>} />;
  }

  return (
    <div className="detail-workspace">
      <PageHeader
        title={String(record.title ?? record.subject ?? record.invoice_number ?? record.prescription_number ?? record.order_number ?? record.ticket_number ?? `Lab order #${id}`)}
        subtitle={formatStatus(String(record.status ?? "n/a"))}
        actions={
          <>
            <Button variant="secondary" onClick={() => navigate("/laboratory")}>Back</Button>
            <Button variant="secondary" onClick={() => void load()}>Refresh</Button>
            
            <Button disabled={busy} onClick={() => { setBusy(true); laboratoriesApi.markCollected(String(id)).then(() => { toast("Marked collected", "success"); void load(); }).catch(() => toast("Failed", "error")).finally(() => setBusy(false)); }}>Mark collected</Button>
            <Button variant="secondary" disabled={busy} onClick={() => { setBusy(true); laboratoriesApi.markReviewed(String(id)).then(() => { toast("Reviewed", "success"); void load(); }).catch(() => toast("Failed", "error")).finally(() => setBusy(false)); }}>Mark reviewed</Button>
            <Button variant="secondary" onClick={() => navigate(`/laboratory/${id}/results`)}>Results</Button>
            
            <Button variant="danger" onClick={() => setConfirmDelete(true)}>Delete</Button>
          </>
        }
      />
      <Tabs active={tab} onChange={setTab} tabs={[
        { id: "overview", label: "Overview" },
        { id: "activity", label: "Activity" },
      ]} />
      {tab === "overview" && (
        <div className="grid-2">
          <Card title="Details">
            <dl className="summary-dl">
              <div><dt>Order #</dt><dd>{String(record.order_number ?? "—")}</dd></div>
              <div><dt>Status</dt><dd>{String(record.status ?? "—")}</dd></div>
              <div><dt>Urgency</dt><dd>{String(record.urgency ?? "—")}</dd></div>
              <div><dt>Notes</dt><dd>{String(record.clinical_notes ?? "—")}</dd></div>
              <div><dt>Created</dt><dd>{formatDateTime(String(record.created_at ?? ""))}</dd></div>
              <div><dt>Updated</dt><dd>{formatDateTime(String(record.updated_at ?? ""))}</dd></div>
            </dl>
          </Card>
          <Card title="Notes">
            <p>{String(record.notes ?? record.description ?? record.clinical_notes ?? record.body ?? record.comment ?? "—")}</p>
          </Card>
        </div>
      )}
      {tab === "activity" && (
        <Card title="Timestamps">
          <p className="muted">Created {formatDateTime(String(record.created_at ?? ""))}</p>
          <p className="muted">Updated {formatDateTime(String(record.updated_at ?? ""))}</p>
        </Card>
      )}
      <ConfirmDialog
        open={confirmDelete}
        title="Delete?"
        message="This cannot be undone."
        confirmLabel="Delete"
        onCancel={() => setConfirmDelete(false)}
        onConfirm={() => { setConfirmDelete(false); void handleDelete(); }}
      />
    </div>
  );
}
