import { Navigate, Route, Routez, useLocation } from "react-router-dom";
import { AppLayout } from "./components/layout/AppLayout";
import { AuthLayout } from "./components/layout/AuthLayout";
import { PageSpinner } from "./components/ui/Spinner";
import { useAuth } from "./hooks/useAuth";

import LoginPage from "./pages/auth/Login";
import RegisterPage from "./pages/auth/Register";
import VerifyEmailPage from "./pages/auth/VerifyEmail";
import ForgotPasswordPage from "./pages/auth/ForgotPassword";
import ResetPasswordPage from "./pages/auth/ResetPassword";
import OnboardingPage from "./pages/auth/Onboarding";

import PatientDashboard from "./pages/dashboard/PatientDashboard";
import DoctorDashboard from "./pages/dashboard/DoctorDashboard";
import StaffDashboard from "./pages/dashboard/StaffDashboard";
import AdminDashboard from "./pages/dashboard/AdminDashboard";

import DoctorSearch from "./pages/discovery/DoctorSearch";
import DoctorProfile from "./pages/discovery/DoctorProfile";
import SpecialtyBrowse from "./pages/discovery/SpecialtyBrowse";
import ClinicDetail from "./pages/discovery/ClinicDetail";

import BookAppointment from "./pages/booking/BookAppointment";
import Appointments from "./pages/booking/Appointments";
import AppointmentDetail from "./pages/booking/AppointmentDetail";
import RescheduleAppointment from "./pages/booking/RescheduleAppointment";
import WaitingList from "./pages/booking/WaitingList";

import VideoRoom from "./pages/consultation/VideoRoom";
import WaitingRoom from "./pages/consultation/WaitingRoom";
import ConsultationNotes from "./pages/consultation/ConsultationNotes";
import ConsultationHistory from "./pages/consultation/ConsultationHistory";

import MedicalRecords from "./pages/medical/MedicalRecords";
import RecordDetail from "./pages/medical/RecordDetail";
import VitalsHistory from "./pages/medical/VitalsHistory";
import Allergies from "./pages/medical/Allergies";
import Medications from "./pages/medical/Medications";

import Prescriptions from "./pages/prescriptions/Prescriptions";
import PrescriptionDetail from "./pages/prescriptions/PrescriptionDetail";
import PharmacyRouting from "./pages/prescriptions/PharmacyRouting";

import LabOrders from "./pages/laboratory/LabOrders";
import LabOrderDetail from "./pages/laboratory/LabOrderDetail";
import LabResults from "./pages/laboratory/LabResults";

import Invoices from "./pages/billing/Invoices";
import InvoiceDetail from "./pages/billing/InvoiceDetail";
import Payments from "./pages/billing/Payments";
import BillingInsurance from "./pages/billing/Insurance";
import Payouts from "./pages/billing/Payouts";

import Messages from "./pages/messaging/Messages";
import ConversationDetail from "./pages/messaging/ConversationDetail";

import ProfileSettings from "./pages/settings/ProfileSettings";
import PrivacySettings from "./pages/settings/PrivacySettings";
import NotificationSettings from "./pages/settings/NotificationSettings";
import OrganizationSettings from "./pages/settings/OrganizationSettings";

import SupportTickets from "./pages/support/SupportTickets";
import TicketDetail from "./pages/support/TicketDetail";
import HelpCenter from "./pages/support/HelpCenter";

import Documents from "./pages/documents/Documents";
import DocumentViewer from "./pages/documents/DocumentViewer";

import Notifications from "./pages/notifications/Notifications";
import InsuranceHub from "./pages/insurance/Insurance";
import InsuranceHubDetail from "./pages/insurance/InsuranceDetail";
import DomainWorkflows from "./pages/platform/DomainWorkflows";

function ProtectedRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, status } = useAuth();
  const location = useLocation();
  if (status === "idle" || status === "loading") return <PageSpinner />;
  if (!isAuthenticated) return <Navigate to="/auth/login" state={{ from: location }} replace />;
  return <>{children}</>;
}

function AuthOnlyRoute({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, status } = useAuth();
  if (status === "idle" || status === "loading") return <PageSpinner />;
  if (isAuthenticated) return <Navigate to="/dashboard" replace />;
  return <>{children}</>;
}

function DashboardRouter() {
  const { user } = useAuth();
  if (!user) return <PageSpinner />;
  switch (user.role) {
    case "doctor":
      return <DoctorDashboard />;
    case "staff":
    case "lab_tech":
    case "pharmacist":
      return <StaffDashboard />;
    case "admin":
      return <AdminDashboard />;
    default:
      return <PatientDashboard />;
  }
}

export default function App() {
  return (
    <Routes>
      <Route path="/auth" element={<AuthLayout />}>
        <Route path="login" element={<AuthOnlyRoute><LoginPage /></AuthOnlyRoute>} />
        <Route path="register" element={<AuthOnlyRoute><RegisterPage /></AuthOnlyRoute>} />
        <Route path="verify-email/:token?" element={<VerifyEmailPage />} />
        <Route path="forgot-password" element={<AuthOnlyRoute><ForgotPasswordPage /></AuthOnlyRoute>} />
        <Route path="reset-password/:token?" element={<ResetPasswordPage />} />
        <Route path="onboarding" element={<ProtectedRoute><OnboardingPage /></ProtectedRoute>} />
      </Route>

      <Route element={<ProtectedRoute><AppLayout /></ProtectedRoute>}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<DashboardRouter />} />
        <Route path="workflows" element={<DomainWorkflows />} />
        <Route path="workflows/:module" element={<DomainWorkflows />} />

        <Route path="discovery" element={<DoctorSearch />} />
        <Route path="doctors" element={<DoctorSearch />} />
        <Route path="discovery/specialties" element={<SpecialtyBrowse />} />
        <Route path="discovery/doctors/:id" element={<DoctorProfile />} />
        <Route path="discovery/clinics/:id" element={<ClinicDetail />} />

        <Route path="appointments" element={<Appointments />} />
        <Route path="appointments/book/:doctorId?" element={<BookAppointment />} />
        <Route path="appointments/:id" element={<AppointmentDetail />} />
        <Route path="appointments/:id/reschedule" element={<RescheduleAppointment />} />
        <Route path="waiting-list" element={<WaitingList />} />

        <Route path="consultations" element={<ConsultationHistory />} />
        <Route path="consultations/:roomId/waiting" element={<WaitingRoom />} />
        <Route path="consultations/:roomId" element={<VideoRoom />} />
        <Route path="consultations/:roomId/notes" element={<ConsultationNotes />} />

        <Route path="medical-records" element={<MedicalRecords />} />
        <Route path="medical-records/:id" element={<RecordDetail />} />
        <Route path="medical-records/vitals" element={<VitalsHistory />} />
        <Route path="medical-records/allergies" element={<Allergies />} />
        <Route path="medical-records/medications" element={<Medications />} />

        <Route path="prescriptions" element={<Prescriptions />} />
        <Route path="prescriptions/:id" element={<PrescriptionDetail />} />
        <Route path="prescriptions/:id/pharmacy" element={<PharmacyRouting />} />

        <Route path="laboratory" element={<LabOrders />} />
        <Route path="laboratory/:id" element={<LabOrderDetail />} />
        <Route path="laboratory/:id/results" element={<LabResults />} />

        <Route path="billing" element={<Invoices />} />
        <Route path="billing/invoices" element={<Invoices />} />
        <Route path="billing/invoices/:id" element={<InvoiceDetail />} />
        <Route path="billing/payments" element={<Payments />} />
        <Route path="billing/insurance" element={<BillingInsurance />} />
        <Route path="billing/payouts" element={<Payouts />} />

        <Route path="messages" element={<Messages />} />
        <Route path="messages/:id" element={<ConversationDetail />} />

        <Route path="settings" element={<ProfileSettings />} />
        <Route path="settings/privacy" element={<PrivacySettings />} />
        <Route path="settings/notifications" element={<NotificationSettings />} />
        <Route path="settings/organization" element={<OrganizationSettings />} />

        <Route path="support" element={<SupportTickets />} />
        <Route path="support/:id" element={<TicketDetail />} />
        <Route path="help" element={<HelpCenter />} />

        <Route path="documents" element={<Documents />} />
        <Route path="documents/:id" element={<DocumentViewer />} />

        <Route path="notifications" element={<Notifications />} />
        <Route path="insurance" element={<InsuranceHub />} />
        <Route path="insurance/:id" element={<InsuranceHubDetail />} />
      </Route>

      <Route path="*" element={<Navigate to="/dashboard" replace />} />
    </Routes>
  );
}
