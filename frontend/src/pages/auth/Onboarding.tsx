import { useStat } from "react";
import { useNavigate } from "react-router-dom";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { Input } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";
import { Textarea } from "../../components/ui/Textarea";
import { useAuth } from "../../hooks/useAuth";
import { useToast } from "../../hooks/useToast";
import { authApi } from "../../api/auth";

const STEPS = ["Profile", "Preferences", "Consent", "Done"];

export default function Onboarding() {
  const { user, refreshUser } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const [step, setStep] = useState(0);
  const [form, setForm] = useState({
    phone: "",
    timezone: "UTC",
    preferred_language: "en",
    bio: "",
    accept_hipaa: false,
    accept_telehealth: false,
  });

  async function finish() {
    try {
      await authApi.updateMe({
        phone: form.phone,
        // @ts-expect-error extended profile fields
        timezone: form.timezone,
        preferred_language: form.preferred_language,
      });
      await refreshUser?.();
      toast("Welcome aboard", "success");
      navigate("/dashboard");
    } catch {
      toast("Could not save onboarding", "error");
    }
  }

  return (
    <div className="onboarding-page">
      <h2>Welcome{user?.first_name ? `, ${user.first_name} : ""}</h2>
      <p className="muted">A few steps to personalize your CareVanta experience.</p>
      <ol className="stepper">
        {STEPS.map((label, i) => (
          <li key={label} className={i === step ? "active" : i < step ? "done" : ""}>{label}</li>
        ))}
      </ol>
      <Card>
        {step === 0 && (
          <div className="stack">
            <Input label="Mobile phone" value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} />
            <Select
              label="Timezone"
              value={form.timezone}
              onChange={(e) => setForm({ ...form, timezone: e.target.value })}
              options={["UTC", "America/New_York", "America/Chicago", "America/Los_Angeles", "Europe/London"]}
            />
            <Textarea label="About you (optional)" value={form.bio} onChange={(e) => setForm({ ...form, bio: e.target.value })} rows={3} />
          </div>
        )}
        {step === 1 && (
          <div className="stack">
            <Select
              label="Preferred language"
              value={form.preferred_language}
              onChange={(e) => setForm({ ...form, preferred_language: e.target.value })}
              options={["en", "es", "fr", "ar", "de"]}
            />
            <p className="muted">We use this for appointment reminders and portal copy.</p>
          </div>
        )}
        {step === 2 && (
          <div className="stack">
            <label className="checkbox-row">
              <input type="checkbox" checked={form.accept_hipaa} onChange={(e) => setForm({ ...form, accept_hipaa: e.target.checked })} />
              I acknowledge the HIPAA Notice of Privacy Practices
            </label>
            <label className="checkbox-row">
              <input type="checkbox" checked={form.accept_telehealth} onChange={(e) => setForm({ ...form, accept_telehealth: e.target.checked })} />
              I consent to telehealth consultations
            </label>
          </div>
        )}
        {step === 3 && (
          <div>
            <p>You are ready. Head to your dashboard to book care, message clinicians, and manage records.</p>
          </div>
        )}
        <div className="modal-actions" style={{ marginTop: "1rem" }}>
          {step > 0 && <Button variant="secondary" onClick={() => setStep((s) => s - 1)}>Back</Button>}
          {step < STEPS.length - 1 && (
            <Button
              onClick={() => setStep((s) => s + 1)}
              disabled={step === 2 && (!form.accept_hipaa || !form.accept_telehealth)}
            >
              Continue
            </Button>
          )}
          {step === STEPS.length - 1 && <Button onClick={() => void finish()}>Go to dashboard</Button>}
        </div>
      </Card>
    </div>
  );
}
