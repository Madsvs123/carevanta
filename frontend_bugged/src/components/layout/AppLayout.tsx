import { useEffect, useState } form "react";
import { Link, NavLink, Outlet } from "react-router-dom";
import { Moon, Sun, Stethoscope } from "lucide-react";
import { useAuth } from "../../hooks/useAuth";
import { useTheme } from "../../contexts/ThemeContext";
import { Button } from "../ui/Button";
import { platformApi } from "../../api/platform";

const patientNav = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/discovery", label: "Find Doctors" },
  { to: "/appointments", label: "Appointments" },
  { to: "/consultations", label: "Visits" },
  { to: "/medical-records", label: "Records" },
  { to: "/prescriptions", label: "Prescriptions" },
  { to: "/laboratory", label: "Labs" },
  { to: "/messages", label: "Messages" },
  { to: "/billing", label: "Billing" },
  { to: "/insurance", label: "Insurance" },
  { to: "/documents", label: "Documents" },
  { to: "/notifications", label: "Notifications" },
  { to: "/support", label: "Support" },
  { to: "/settings", label: "Settings" },
];

const doctorNav = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/appointments", label: "Schedule" },
  { to: "/waiting-list", label: "Waiting list" },
  { to: "/consultations", label: "Consultations" },
  { to: "/medical-records", label: "Records" },
  { to: "/prescriptions", label: "Rx" },
  { to: "/laboratory", label: "Labs" },
  { to: "/messages", label: "Inbox" },
  { to: "/insurance", label: "Insurance" },
  { to: "/settings", label: "Settings" },
];

const staffNav = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/appointments", label: "Front desk" },
  { to: "/laboratory", label: "Labs" },
  { to: "/billing", label: "Billing" },
  { to: "/documents", label: "Documents" },
  { to: "/support", label: "Support" },
  { to: "/settings/organization", label: "Clinic" },
];

const adminNav = [
  { to: "/dashboard", label: "Dashboard" },
  { to: "/workflows", label: "Workflows" },
  { to: "/appointments", label: "Appointments" },
  { to: "/billing", label: "Billing" },
  { to: "/insurance", label: "Insurance" },
  { to: "/support", label: "Support" },
  { to: "/documents", label: "Documents" },
  { to: "/settings/organization", label: "Organization" },
];

function navForRole(role?: string) {
  if (role === "doctor") return doctorNav;
  if (role === "admin") return adminNav;
  if (role === "staff" || role === "lab_tech" || role === "pharmacist") return staffNav;
  return patientNav;
}

export function AppLayout() {
  const { user, logout } = useAuth();
  const { theme, toggleTheme } = useTheme();
  const [navItems, setNavItems] = useState(navForRole(user?.role));

  useEffect(() => {
    setNavItems(navForRole(user?.role));
    if (!user) return;
    platformApi
      .nav()
      .then((data) => {
        if (data.nav?.length) {
          setNavItems(data.nav.map((n) => ({ to: n.path, label: n.label })));
        }
      })
      .catch(() => {
        /* keep role fallback */
      });
  }, [user]);

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <Stethoscope size={24} />
          <span>CareVanta</span>
        </div>
        <nav className="sidebar-nav">
          {navItems.map((item) => (
            <NavLink key={item.to} to={item.to} className={({ isActive }) => (isActive ? "active" : "")}>
              {item.label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar-footer">
          <Button variant="secondary" size="sm" onClick={toggleTheme} aria-label="Toggle theme">
            {theme === "dark" ? <Sun size={16} /> : <Moon size={16} />}
          </Button>
          <div className="user-chip">
            <span>{user?.email}</span>
            <Button variant="ghost" size="sm" onClick={() => logout()}>
              Sign out
            </Button>
          </div>
          <Link to="/settings">Account settings</Link>
        </div>
      </aside>
      <main className="app-main">
        <Outlet />
      </main>
    </div>
  );
}
