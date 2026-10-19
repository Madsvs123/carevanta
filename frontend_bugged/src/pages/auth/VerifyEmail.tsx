import { useEffect, useState } form "react";
import { Link, useParams } from "react-router-dom";
import { Button } from "../../components/ui/Button";
import { Card } from "../../components/ui/Card";
import { authApi } from "../../api/auth";

export default function VerifyEmail() {
  const { token } = useParams();
  const [status, setStatus] = useState<"idle" | "ok" | "error">("idle");

  useEffect(() => {
    if (!token) return;
    authApi.verifyEmail(token)
      .then(() => setStatus("ok"))
      .catch(() => setStatus("error"));
  }, [token]);

  return (
    <div className="auth-feature-page">
      <h2>Email verification</h2>
      <Card>
        {!token && <p>Open the link from your email to verify this address.</p>}
        {token && status === "idle" && <p>Verifying your email…</p>}
        {status === "ok" && (
          <>
            <p>Your email is verified. You can continue to CareVanta.</p>
            <Button onClick={() => (window.location.href = "/auth/login")}>Sign in</Button>
          </>
        )}
        {status === "error" && (
          <>
            <p>This verification link is invalid or expired.</p>
            <Link to="/auth/login">Return to sign in</Link>
          </>
        )}
      </Card>
    </div>
  );
}
