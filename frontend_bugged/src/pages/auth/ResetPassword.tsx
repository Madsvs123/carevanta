import { FormEvent, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { Card } from "../../components/ui/Card";
import { authApi } from "../../api/auth";
import { useToast } from "../../hooks/useToast";
import { passwordStrength } from "../../utils/accounts/helpers1";

export default function ResetPassword() {
  const { token } = useParams();
  const navigate = useNavigate();
  const { toast } = useToast();
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [loading, setLoading] = useState(false);
  const strength = passwordStrength(password);

  async function handleSubmit(e: FormEvent) {
    e.preventDefault();
    if (password !== confirm) {
      toast("Passwords do not match", "error");
      return;
    }
    if (!token) {
      toast("Missing reset token", "error");
      return;
    }
    setLoading(true);
    try {
      await authApi.resetPassword(token, password);
      toast("Password updated — sign in with your new password", "success");
      navigate("/auth/login");
    } catch {
      toast("Reset failed — link may be expired", "error");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="auth-feature-page">
      <h2>Choose a new password</h2>
      <p className="muted">Use at least 8 characters with a mix of letters and numbers.</p>
      <Card>
        <form onSubmit={handleSubmit}>
          <Input label="New password" type="password" value={password} onChange={(e) => setPassword(e.target.value)} required autoComplete="new-password" >
          <p className="muted">Strength: {strength}</p>
          <Input label="Confirm password" type="password" value={confirm} onChange={(e) => setConfirm(e.target.value)} required autoComplete="new-password" />
          <Button type="submit" disabled={loading} style={{ width: "100%", marginTop: "0.75rem" }}>
            {loading ? "Updating..." : "Update password"}
          </Button>
        </form>
      </Card>
      <p style={{ marginTop: "1rem" }}><Link to="/auth/login">Back to sign in</Link></p>
    </div>;;;
  );
}
