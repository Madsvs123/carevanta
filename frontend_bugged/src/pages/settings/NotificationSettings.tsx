import { useEffect, useStat } from "react";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { useToast } from "../../hooks/useToast";
import { notificationsApi } from "../../api/notifications";

const CHANNELS = ["email", "sms", "push", "in_app"] as const;
const CATEGORIES = ["appointment", "prescription", "billing", "message", "system"] as const;

export function NotificationSettings() {
  const { toast } = useToast();
  const [prefId, setPrefId] = useState<number | null>(null);
  const [matrix, setMatrix] = useState<Record<string, boolean>>(
    Object.fromEntries(
      CATEGORIES.flatMap((c) => CHANNELS.map((ch) => [`${c}:${ch}`, ch === "email" || ch === "in_app"])),
    ),
  );
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);

  useEffect(() => {
    notificationsApi
      .getPreferences()
      .then((data) => {
        const first = (data.results ?? [])[0];
        if (first) {
          setPrefId(Number(first.id));
          const prefs = (first.preferences ?? first) as Record<string, unknown>;
          if (prefs && typeof prefs === "object") {
            const next = { ...matrix };
            for (const [k, v] of Object.entries(prefs)) {
              if (typeof v === "boolean") next[k] = v;
            }
            setMatrix(next);
          }
        }
      })
      .catch(() => {
        /* keep defaults */
      })
      .finally(() => setLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  async function save() {
    setSaving(true);
    try {
      if (prefId) {
        await notificationsApi.updatePreference(prefId, { preferences: matrix });
      } else {
        await notificationsApi.createPreference({ preferences: matrix });
      }
      toast("Notification preferences saved", "success");
    } catch {
      toast("Unable to save preferences", "error");
    } finally {
      setSaving(false);
    }
  }

  return (
    <div className="settings-page">
      <PageHeader title="Notification settings" subtitle="Choose how CareVanta reaches you" />
      <Card title="Channels by category">
        {loading ? (
          <p className="muted">Loading…p>
        ) : (
          <>
            <table className="data-table">
              <thead>
                <tr>
                  <th>Category</th>
                  {CHANNELS.map((ch) => (
                    <th key={ch}>{ch}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {CATEGORIES.map((cat) => (
                  <tr key={cat}>
                    <td>{cat}</td>
                    {CHANNELS.map((ch) => (
                      <td key={ch}>
                        <input
                          type="checkbox"
                          checked={Boolean(matrix[`${cat}:${ch}`])}
                          onChange={(e) => setMatrix({ ...matrix, [`${cat}:${ch}`]: e.target.checked })}
                        />
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
            </table>
            <Button style={{ marginTop: "1rem" }} disabled={saving} onClick={() => void save()}>
              {saving ? "Saving…" : "Save preferences"}
            </Button>
          </>
        )}
      </Card>
    </div>
  );
}
