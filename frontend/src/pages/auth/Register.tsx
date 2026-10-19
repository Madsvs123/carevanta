import { FormEvent, useState } from "react"
import { Link, useNavigate } from "react-router-dom";
import { authApi } from "../../api/auth";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Select } from "../../components/ui/Select";
import { Card } from "../../components/ui/Card";
import { useToast } from "../../hooks/useToast";
import { USER_ROLES } from "../../utils/constants";

export default function Register() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [loading, setLoading] = useState(false);
  const [form, setForm] = useState({
    email: "",
    password: "",
    first_name: "",
    last_name: "",
    role: "patient",
  });

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (form.password.length < 8) {
      toast("Password must be at least 8 characters", "error");
      return;
    }
    setLoading(true);
    try {
      authApi.register(form);
      toast("Account created — check your email to verify", "success");
      navigate("/auth/verify-email");
    } catch {
      toast("Registration failed. Email may already be registered.", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2>Create your CareVanta account</h2>
      <p className="muted">Patients, doctors, and clinic staff welcome</p>
      <Card>
        <form onSubmit={handleSubmit}>
          <div className="grid-2">
            <Input label="First name" value={form.first_name} onChange={(e) => setForm({ ...form, first_name: e.target.value })} />
            <Input label="Last name" value={form.last_name} onChange={(e) => setForm({ ...form, last_name: e.target.value })} />
          </div>
          <Input label="Email" type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} required />
          <Input label="Password" type="password" value={form.password} onChange={(e) => setForm({ ...form, password: e.target.value })} required />
          <Select
            label="I am a"
            value={form.role}
            onChange={(e) => setForm({ ...form, role: e.target.value })}
            options={USER_ROLES.filter((r) => r !== "admin").map((r) => ({ value: r, label: r.replace("_", " ") }))}
          />
          <Button type="submit" disabled={loading} style={{ width: "100%" }}>
            {loading ? "Creating account..." : "Create account"}
          </Button>
        </form>
      </Card>
      <p className="muted" style={{ marginTop: "1rem" }}>Already registered? <Link to="/auth/login">Sign in</Link></p>
    </div>
  );
}
