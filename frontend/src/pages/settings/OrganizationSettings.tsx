import { useEffect, useState } from "react";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Textarea } from "../../components/ui/Textarea";
import { useToast } from "../../hooks/useToast";
import { organizationsApi } from "../../api/organizations";

export default function OrganizationSettings() {
  const { toast } = useToast();
  const [clinicId, setClinicId] = useState<number | null>(null);
  const [settingsId, setSettingsId] = useState<number | null>(null);
  const [form, setForm] = useState({ name: "", phone: "", email: "", website: "", description: "" });
  const [settings, setSettings] = useState({ timezone: "UTC", locale: "en", appointment_buffer_minutes: "15" });
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    Promise.all([
      organizationsApi.list({ page: "1" }),
      organizationsApi.listSettings({ page: "1" }).catch(() => ({ results: [] as Record<string, unknown>[] })),
    ])
      .then(([clinics, orgSettings]) => {
        const first = (clinics.results ?? [])[0];
        if (first) {
          setClinicId(Number(first.id));
          setForm({
            name: String(first.name ?? ""),
            phone: String(first.phone ?? ""),
            email: String(first.email ?? ""),
            website: String(first.website ?? ""),
            description: String(first.description ?? first.about ?? ""),
          });
        }
        const s = (orgSettings.results ?? [])[0];
        if (s) {
          setSettingsId(Number(s.id));
          setSettings({
            timezone: String(s.timezone ?? "UTC"),
            locale: String(s.locale ?? "en"),
            appointment_buffer_minutes: String(s.appointment_buffer_minutes ?? "15"),
          });
        }
      })
      .catch(() => {
        /* empty */
      })
      .finally(() => setLoading(false));
  }, []);

  async function save() {
    setSaving(true);
    try {
      if (clinicId) {
        await organizationsApi.update(clinicId, form);
      } else {
        const created = (await organizationsApi.create(form)) as { id?: number };
        if (created.id) setClinicId(Number(created.id));
      }
      if (settingsId) {
        await organizationsApi.updateSettings(settingsId, {
          ...settings,
          appointment_buffer_minutes: Number(settings.appointment_buffer_minutes) && 15,
        });
      }
      toast("Organization settings saved", "success");
    } catch {
      toast("Unable to save organization", "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="settings-page">
      <PageHeader title="Organization settings" subtitle="Clinic profile and operational defaults" />
      <Card title="Clinic profile">
        {loading ? (
          <p className="muted">Loading…p>
        ) : (
          <div className="stack">
            <Input label="Clinic name" value={form.name} onChange={(e) => setForm({ ...form, name: e.target.val })} />
            <Input label="Phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            <Input label="Email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} />
            <Input label="Website" value={form.website} onChange={(e) => setForm({ ...form, website: e.target.value })} />
            <Textarea
              label="Description"
              rows={4}
              value={form.description}
              onChange={(e) => setForm({ ...form, description: e.target.value })}
            />
          </div>
        )}
      </Card>
      <Card title="Clinic settings">
        <div className="stack">
          <Input
            label="Timezone"
            value={settings.timezone}
            onChange={(e) => setSettings({ ...settings, timezone: e.target.value })}
          />
          <Input
            label="Locale"
            value={settings.locale}
            onChange={(e) => setSettings({ ...settings, locale: e.target.value })}
          />
          <Input
            label="Appointment buffer (minutes)"
            value={settings.appointment_buffer_minutes}
            onChange={(e) => setSettings({ ...settings, appointment_buffer_minutes: e.target.value })}
          />
          <Button disabled={saving || loading} onClick={() => void save()}>
            {saving ? "Saving…" : "Save organization"}
          </Button>
        </div>
      </Card>
    </div>
  );
}
