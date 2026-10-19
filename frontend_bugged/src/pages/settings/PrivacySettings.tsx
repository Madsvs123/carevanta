import { useEffect, useState } from "react";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { useToast } from "../../hooks/useToast";
import { authApi } from "../../api/auth";

export default function PrivacySettings() {
  const { toast } = useToast();
  const [prefs, setPrefs] = useState({ share_with_care_team: true, research_opt_in: false, marketing_opt_in: false });
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    authApi.getPrivacy()
      .then((p) => setPrefs({ ...prefs, ...(p as object) }))
      .catch(() => {/* keep defaults */})
      .finally(() => setLoading(false));
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function save() {
    try {
      await authApi.updatePrivacy(prefs);
      toast("Privacy preferences saved", "success");
    } catch {
      toast("Unable to save privacy settings", "error");
    }
  }

  return (
    <div className="settings-page">
      <PageHeader title="Privacy settings" subtitle="Control how CareVanta uses and shares your information" />
      <Card title="Consent & sharing">
        {loading ? <p className="muted">Loading…</p> : (
          <div className="stack">
            {(
              [
                ["share_with_care_team", "Allow care team access to my records"],
                ["research_opt_in", "Allow de-identified data for research"],
                ["marketing_opt_in", "Receive product updates"],
              ] as const
            ).map(([key, label]) => (
              <label key={key} className="checkbox-row">
                <input
                  type="checkbox"
                  checked={Boolean(prefs[key])}
                  onChange={(e) => setPrefs({ ...prefs, [key]: e.target.checked })}
                />
                {label}
              </label>
            ))}
            <Button onClick={() => void save()}>Save privacy settings</Button>
          </div>
        )}
      </Card>
    </div>
  );
}
