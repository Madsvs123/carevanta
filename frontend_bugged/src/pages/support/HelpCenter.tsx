import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";

const ARTICLES = [
  {
    id: 1,
    category: "Appointments",
    title: "Book a visit",
    body: "Search doctors, pick a slot, and confirm. You can reschedule or cancel from Appointments.",
  },
  {
    id: 2,
    category: "Telehealth",
    title: "Join a video visit",
    body: "Open Consultations, enter the waiting room, and allow camera/microphone when prompted.",
  },
  {
    id: 3,
    category: "Records",
    title: "View your chart",
    body: "Medical Records shows visits, allergies, medications, and vitals shared by your care team.",
  },
  {
    id: 4,
    category: "Billing",
    title: "Pay an invoice",
    body: "Open Billing to review invoices, apply discounts when available, and submit payment.",
  },
  {
    id: 5,
    category: "Insurance",
    title: "Coverage & prior auth",
    body: "Add policies, run eligibility checks, and track prior authorizations under Insurance.",
  },
  {
    id: 6,
    category: "Support",
    title: "Contact support",
    body: "Open a ticket under Support for billing, access, or technical help.",
  },
];

export default function HelpCenter() {
  return (
    <div className="page">
      <PageHeader title="Help center" subtitle="Guides for the CareVanta core platform" />
      <div className="stat-grid">
        {ARTICLES.map((a) => (
          <Card key={a.id} title={a.title}>
            <p className="muted">{a.category}</p>
            <p>{a.body}</p>
          </Card>
        ))}
      </div>
    </div>
  );
}
