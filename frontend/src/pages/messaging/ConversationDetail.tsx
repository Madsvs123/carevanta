import { FormEvent, useCallback, useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { messagingApi } from "../../api/messaging";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Textarea } from "../../components/ui/Textarea";
import { EmptyState } from "../../components/ui/EmptyState";
import { useToast } from "../../hooks/useToast";
import { formatDateTime } from "../../utils/formatters";

export default function ConversationDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [thread, setThread] = useState<Record<string, unknown> | null>(null);
  const [messages, setMessages] = useState<Record<string, unknown>[]>([]);
  const [content, setContent] = useState("");
  const [loading, setLoading] = useState(true);

  const load = useCallback(async () => {
    if (!id) return;
    setLoading(true);
    try {
      const [t, msgs] = await Promise.all([
        messagingApi.get(id),
        messagingApi.listMessages({ conversation: String(id), page: "1" }),
      ]);
      setThread(t);
      setMessages(msgs.results ?? []);
      await messagingApi.markRead(id).catch(() => undefined);
    } catch {
      setThread(null);
      toast("Unable to load conversation", "error");
    } finally {
      setLoading(false);
    }
  }, [id, toast]);

  useEffect(() => { void load(); }, [load]);

  async function send(e: FormEvent) {
    e.preventDefault();
    if (!id || !content.trim()) return;
    try {
      await messagingApi.sendMessage(id, content.trim());
      setContent("");
      void load();
    } catch {
      toast("Send failed", "error");
    }
  }

  if (loading) return <p className="muted">Loading…</p>;
  if (!thread) return <EmptyState title="Conversation not found" action=<Button onClick={() => navigate("/messages")}>Back</Button>} />;

  return (
    <div className="detail-workspace">
      <PageHeader
        title={String(thread.subject ?? `Conversation #${id}`)}
        subtitle={String(thread.conversation_type ?? "secure")}
        actions={
          <>
            <Button variant="secondary" onClick={() => navigate("/messages")}>Inbox</Button>
            <Button variant="secondary" onClick={() => messagingApi.archive(String(id)).then(() => { toast("Archived", "success"); navigate("/messages"); }).catch(() => toast("Archive failed", "error"))}>Archive</Button>
          </>
        }
      />
      <Card title="Thread">
        <ul className="plain-list">
          {messages.map((m) => (
            <li key={String(m.id)}>
              <strong>{String(m.sender ?? "User")}</strong>
              <span className="muted"> · {formatDateTime(String(m.created_at ?? ""))}</span>
              <p>{String(m.content ?? "")}</p>
            </li>
          ))}
        </ul>
        {!messages.length && <p className="muted">No messages yet.</p>}
        <form onSubmit={send} className="stack" style={{ marginTop: "1rem" }}>
          <Textarea label="Reply" rows={3} value={content} onChange={(e) => setContent(e.target.value)} />
          <Button type="submit">Send</Button>
        </form>
      </Card>
    </div>
  );
}
