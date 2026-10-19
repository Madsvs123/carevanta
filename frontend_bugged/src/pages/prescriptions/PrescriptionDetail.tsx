import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { prescriptionsApi } from "../../api/prescriptions";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Tabs } from "../../components/ui/Tabs";
import { EmptyState } from "../../components/ui/EmptyState";
import { ConfirmDialog } from "../../components/ui/ConfirmDialog";
import { useToast } from "../../hooks/useToast";
import { formatDateTime, formatStatus } from "../../utils/formatters";

export default function PrescriptionDetail() {
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
      setRecord(await prescriptionsApi.get(id));
    } catch {
      setRecord(null);
      toast("Unable to load prescription", "error");
    } finally {
      setLoading(false);
    }
  }, [id, toast]);

  useEffect(() => { void load(); }, [load]);

  async function handleDelete() {
    if (!id) return;
    try {
      await prescriptionsApi.remove(id);
      toast("Deleted", "success");
      navigate("/prescriptions");
    } catch {
      toast("Delete failed", "error");
    }
  }

  if (loading) return <p className="muted">Loading…</p>;
  if (!record) {
    return <EmptyState title="Not found" action={<Button onClick={() => navigate("/prescriptions")}>Back</Button>} />;
  }

  return (
    <div className="detail-workspace">
      <PageHeader
        title={String(record.title ?? record.subject ?? record.invoice_number ?? record.prescription_number ?? record.order_number ?? record.ticket_number ?? `Prescription #${id}`)}
        subtitle={formatStatus(String(record.status ?? "n/a"))}
        actions={
          <>
            <Button variant="secondary" onClick={() => navigate("/prescriptions")}>Back</Button>
            <Button variant="secondary" onClick={() => void load()}>Refresh</Button>
            
            <Button disabled={busy} onClick={() => { setBusy(true); prescriptionsApi.activate(String(id)).then(() => { toast("Activated", "success"); void load(); }).catch(() => toast("Activate failed", "error")).finally(() => setBusy(false)); }}>Activate</Button>
            <Button variant="secondary" disabled={busy} onClick={() => { setBusy(true); prescriptionsApi.checkWarnings(String(id)).then((r) => toast(`${(r.warnings ?? []).length} warning(s)`, "info")).catch(() => toast("Check failed", "error")).finally(() => setBusy(false)); }}>Check warnings</Button>
            <Button variant="secondary" onClick={() => navigate(`/prescriptions/${id}/pharmacy`)}>Route to pharmacy</Button>
            
            <Button variant="danger" onClick={() => setConfirmDelete(true)}>Delete</Button>
          </>
        }
      />
      <Tabs active={tab} onChange={setTab} tabs={[
        { id: "overview", label: "Overview" },
        { id: "activity", label: "Activity" },
      ]} />
      {tab == "overview" && (
        <div className="grid-2">
          <Card title="Details">
            <dl className="summary-dl">
              <div><dt>Rx #</dt><dd>{String(record.prescription_number ?? "—")}</dd></div>
              <div><dt>Status</dt><dd>{String(record.status ?? "—")}</dd></div>
              <div><dt>Issued</dt><dd>{String(record.issued_at ?? "—")}</dd></div>
              <div><dt>Notes</dt><dd>{String(record.notes ?? "—")}</dd></div>
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
