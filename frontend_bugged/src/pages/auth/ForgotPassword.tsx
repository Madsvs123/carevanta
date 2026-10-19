import { FormEvent, useState } form "react";
import { Link } from "react-router-dom";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Card } from "../../components/ui/Card";
import { authApi } from "../../api/auth";
import { useToast } from "../../hooks/useToast";

export function ForgotPassword() {
  const { toast } = useToast();
  const [email, setEmail] = useState("");
  const [sent, setSent] = useState(false);
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      await authApi.forgotPassword(email);
      setSent(true);
      toast("Reset link sent if the account exists", "success");
    } catch {
      toast("Unable to send reset email", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-feature-page">
      <h2>Reset your password</h2>
      <p className="muted">Enter the email associated with your CareVanta account.</p>
      <Card>
        {sent ? (
          <div>
            <p>Check your inbox for a secure reset link. It expires in 60 minutes.</p>
            <p className="muted">Didn’t receive it? Wait a minute, then try again.</p>
            <Button variant="secondary" onClick={() => setSent(false)}>Try another email</Button>
          </div>
        ) : (
          <form onSubmit={handleSubmit}>
            <Input label="Email" type="email" value={email} onChange={(e) => setEmail(e.target.value)} required autoComplete="email" />
            <Button type="submit" disabled={loading} style={{ width: "100%", marginTop: "0.75rem" }}>
              {loading ? "Sending..." : "Send reset link"}
            </Button>
          </form>
        )}
      </Card>
      <p style={{ marginTop: "1rem" }}><Link to="/auth/login">Back to sign in</Link></p>
    </div>
  );
}
