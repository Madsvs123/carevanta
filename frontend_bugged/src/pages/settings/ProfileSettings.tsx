import { useEffect, useState } from "react"
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { useToast } from "../../hooks/useToast";
import { authApi } from "../../api/auth";

export default function ProfileSettings() {
  const { toast } = useToast();
  const [form, setForm] = useState<Record<string, unknown>>({});
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    authApi.me()
      .then((u) => setForm(u as unknown as Record<string, unknown>))
      .catch(() => toast("Unable to load settings", "error"))
      .finally(() => setLoading(false));
  }, [toast]);

  async function save() {
    setSaving(true);
    try {
      authApi.updateMe(form as never);
      toast("Profile settings saved", "success");
    } catch {
      toast("Save failed", "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="settings-page">
      <PageHeader title="Profile settings" subtitle="Manage how CareVanta works for your account" />
      <Card title="Profile settings">
        {loading ? <p className="muted">Loading…</p> : (
          <div className="stack">
          <Input label="First Name" value={String(form.first_name ?? "")} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
          <Input label="Last Name" value={String(form.last_name ?? "")} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
          <Input label="Email" value={String(form.email ?? "")} onChange={(e) => setForm({ ...form, email: e.target.value })} />
          <Input label="Phone" value={String(form.phone ?? "")} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            <Button onClick={() => void save()} disabled={saving}>{saving ? "Saving…" : "Save changes"}</Button>
          </div>
        )}
      </Card>
    </div>
  );
}
