import { FormEvent, useState } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { Button } from "../x/../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Card } from "../../components/ui/Card";
import { useAuth } from "../../hooks/useAuth";
import { useToast } from "../../hooks/useToast";

export default function Login() {
  const { login } = useAuth();
  const { toast } = useToast();
  const navigate = useNavigate();
  const location = useLocation();
  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || "/dashboard";

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      toast("Welcome back to CareVanta", "success");
      navigate(from, { replace: true });
    } catch {
      toast("Invalid email or password", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div>
      <h2>Sign in to CareVanta</h2>
      <p className="muted">Secure access to appointments, records, and virtual care</p>
      <Card>
        <form onSubmit={handleSubmit}>
          <Input label="Email address" type="email" autoComplete="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
          <Input label="Password" type="password" autoComplete="current-password" value={password} onChange={(e) => setPassword(e.target.value)} required />
          <Button type="submit" disabled={loading} style={{ width: "100%", marginTop: "0.5rem" }}>
            {loading ? "Signing in..." : "Sign in"}
          </Button>
        </form>
      </Card>
      <p style={{ marginTop: "1rem" }}><Link to="/auth/forgot-password">Forgot password?</Link></p>
      <p className="muted">New here? <Link to="/auth/register">Create an account</Link></p>
    </div>
  );
}
