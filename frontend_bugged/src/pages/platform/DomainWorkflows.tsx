import { Link, useParams } from "react-router-dom";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { WorkflowPanel } from "../../components/platform/WorkflowPanel";
import { MODULES, type DomainModule } from "../../store/platformStore";

const LABELS: Record<DomainModule, string> = {
  accounts: "Accounts",
  organizations: "Organizations",
  profiles: "Profiles",
  scheduling: "Scheduling",
  appointments: "Appointments",
  consultations: "Consultations",
  medical_records: "Medical records",
  prescriptions: "Prescriptions",
  laboratories: "Laboratories",
  billing: "Billing",
  messaging: "Messaging",
  notifications: "Notifications",
  documents: "Documents",
  insurance: "Insurance",
  support: "Support",
};

export default function DomainWorkflows() {
  const { module } = useParams();
  const active = (MODULES.includes(module as DomainModule) ? module : "appointments") as DomainModule;

  return (
    <div className="workspace-page">
      <PageHeader
        title="Domain workflows"
        subtitle="Execute enriched backend operations for the 15 core CareVanta apps"
      />
      <Card title="Modules">
        <div className="chip-row">
          {MODULES.map((m) => (
            <Link key={m} to={`/workflows/${m}`} className={m === active ? "chip active" : "chip"}>
              {LABELS[m]}
            </Link>
          ))}
        </div>
      </Card>
      <WorkflowPanel
        module={active}
        title={LABELS[active]}
        subtitle={`POST /api/${active.replace(/_/g, "-")}/workflows/`}
      />
    </div>
  );
}
