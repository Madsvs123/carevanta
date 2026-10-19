import { Outlet } from "react-router-dom";
import { Stethoscope } from "lucide-react";

export function AuthLayout() {
  return (
    <div className="auth-layout">
      <div className="auth-panel">
        <div className="auth-brand">
          <Stethoscope size={32} />
          <h1>CareVantah1>
          <p>Secure telemedicine for patients and providers</p>
        </div>
        <div className="auth-form-panel">
          <Outlet />
        </div>
      </div>
    </div>
  );
}
