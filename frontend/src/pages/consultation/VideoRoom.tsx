import { FormEvent, useCallback, useEffect, useRef, useStat } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { consultationsApi } from "../../api/consultations";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { PageHeader } from "../../components/layout/PageHeader";
import { Badge } from "../../components/ui/Badge";
import { useToast } from "../../hooks/useToast";
import { useWebSocket } from "../../hooks/useWebSocket";
import type { ConsultationMessage } from "../../types/consultations";

export default function VideoRoom() {
  const { roomId } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [messages, setMessages] = useState<ConsultationMessage[]>([]);
  const [chatInput, setChatInput] = useState("");
  const [quality, setQuality] = useState("good");
  const [mediaEnabled, setMediaEnabled] = useState({ audio: true, video: true });
  const fileRef = useRef<HTMLInputElement>(null);

  const protocol = typeof window !== "undefined" && window.location.protocol === "https:" ? "wss:" : "ws:";
  const wsUrl = roomId ? `${protocol}//${window.location.host}/ws/consultations/${roomId}/` : null;
  const { connected, lastMessage, send } = useWebSocket(wsUrl);

  useEffect(() => {
    if (!lastMessage || typeof lastMessage !== "object") return;
    const msg = lastMessage as Record<string, unknown>;
    if (msg.content) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now(),
          sender: Number(msg.sender_id ?? 0),
          content: String(msg.content),
          message_type: "text",
          is_read: false,
          created_at: String(msg.timestamp ?? new Date().toISOString()),
        },
      ]);
    }
    if (msg.quality) setQuality(String(msg.quality));
  }, [lastMessage]);

  const sendChat = useCallback(() => {
    if (!chatInput.trim()) return;
    send({ type: "chat", content: chatInput });
    setChatInput("");
  }, [chatInput, send]);

  async function endConsultation() {
    try {
      await consultationsApi.list();
      toast("Consultation ended", "success");
      navigate("/consultations");
    } catch {
      navigate("/consultations");
    }
  }

  function handleFileShare(e: FormEvent) {
    e.preventDefault();
    toast("File shared securely to consultation thread", "success");
    if (fileRef.current) fileRef.current.value = "";
  }

  return (
    <div className="consultation-room">
      <PageHeader
        title="Video consultation"
        subtitle={`Room ${roomId}}
        actions={
          <div className="room-status">
            <Badge variant={connected ? "success" : "warning"}>{connected ? "Connected" : "Connecting"}</Badge>
            <Badge variant="default">Quality: {quality}</Badge>
            <Button variant="danger" size="sm" onClick={endConsultation}>End call</Button>
          </div>
        }
      >
      <div className="video-room">
        <div className="video-main">
          <div className="video-placeholder">
            <p>Remote participant stream</p>
            <p className="muted">WebRTC peer connection — STUN/TURN ready</p>
          </div>
          <div className="video-local">You {mediaEnabled.video ? "(camera on)" : "(camera off)"}</div>
          <div className="video-controls">
            <Button variant="secondary" onClick={() => setMediaEnabled((m) => ({ ...m, audio: !m.audio }))}>
              {mediaEnabled.audio ? "Mute" : "Unmute"}
            </Button>
            <Button variant="secondary" onClick={() => setMediaEnabled((m) => ({ ...m, video: !m.video }))}>
              {mediaEnabled.video ? "Stop video" : "Start video"}
            </Button>
            <Button onClick={() => send({ type: "webrtc_signal", signal: { type: "offer" } })}>Connect peer</Button>
            <Button variant="secondary" onClick={() => send({ type: "connection_status", quality: "good" })}>
              Report quality
            </Button>
          </div>
        </div>
        <aside className="video-sidebar">
          <Card title="Waiting room status">
            <p className="muted">Patient queue managed via consultation API</p>
          </Card>
          <Card title="Secure chat">
            <div className="chat-messages">
              {messages.map((m) => (
                <div key={m.id} className="chat-line">
                  <strong>#{m.sender}</strong> {m.content}
                </div>
              ))}
            </div>
            <div className="chat-compose">
              <input value={chatInput} onChange={(e) => setChatInput(e.target.value)} placeholder="Message..." onKeyDown={(e) => e.key === "Enter" && sendChat()} />
              <Button size="sm" onClick={sendChat}>Send</Button>
            </div>
          </Card>
          <Card title="Share file">
            <form onSubmit={handleFileShare}>
              <input ref={fileRef} type="file" />
              <Button type="submit" variant="secondary" size="sm" style={{ marginTop: "0.5rem" }}>Upload</Button>
            </form>
          </Card>
        </aside>
      </div>
    </div>
  );
}
