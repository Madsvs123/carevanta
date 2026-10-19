import { useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { documentsApi } from "../../api/documents";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { EmptyState } from "../../components/ui/EmptyState";
import { useToast } from "../../hooks/useToast";
import { formatDateTime } from "../../utils/formatters";

export default function DocumentViewer() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [doc, setDoc] = useState<Record<string, unknown> | null>(null);
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      setDoc(await documentsApi.get(id));
    } catch {
      setDoc(null);
      toast("Unable to load document", "error");
    } finally {
      setLoading(false);
    }
  }, [id, toast]);

  useEffect(() => {
    void load();
  }, [load]);

  if (loading) return <p className="muted">Loading…</p>;
  if (!doc) {
    return (
      <EmptyState title="Document not found" action={<Button onClick={() => navigate("/documents")}>Back</Button>} />
    );
  }

  return (
    <div className="detail-workspace">
      <PageHeader
        title={String(doc.title ?? doc.filename ?? `Document #${id}`)}
        subtitle={String(doc.category ?? "")}
        actions={
          <Button variant="secondary" onClick={() => navigate("/documents")}>
            Back
          </Button>
        }
      />
      <Card title="File details">
        <dl className="summary-dl">
          <div>
            <dt>Filename</dt>
            <dd>{String(doc.filename ?? "—")}</dd>
          </div>
          <div>
            <dt>Size</dt>
            <dd>{String(doc.file_size ?? "—")}</dd>
          </div>
          <div>
            <dt>Uploaded</dt>
            <dd>{formatDateTime(String(doc.created_at ?? ""))}</dd>
          </div>
        </dl>
        {doc.file_url ? (
          <p>
            <a href={String(doc.file_url)} target="_blank" rel="noreferrer">
              Open file
            </a>
          </p>
        ) : (
          <p className="muted">No downloadable URL on this record.</p>
        )}
      </Card>
    </div>
  );
}
