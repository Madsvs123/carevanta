export interface Appointment {
  id: number;
  patient: number;
  doctor: number;
  doctor_name: string;
  patient_name: string;
  slot?: number;
  scheduled_start: string;
  scheduled_end: string;
  status: string;
  appointment_type: string;
  consultation_type: string;
  reason_for_visit: string;
  symptoms?: string;
  notes?: string;
  checked_in_at?: string;
  cancelled_at?: string;
  cancellation_reason?: string;
  is_follow_up?: boolean;
  created_at?: string;
}

export interface WaitingListEntry {
  id: number;
  doctor: number;
  preferred_date_start?: string;
  preferred_date_end?: string;
  reason?: string;
  status: string;
  priority: number;
  offered_slot?: number;
  created_at?: string;
}

export interface AvailabilitySlot {
  id: number;
  doctor: number;
  start_datetime: string;
  end_datetime: string;
  duration_minutes: number;
  status: string;
  consultation_type: string;
}
