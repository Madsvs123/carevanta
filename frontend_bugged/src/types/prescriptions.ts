export interface Prescription {
  id: number;
  prescription_number?: string;
  patient?: number;
  doctor?: number;
  status: string;
  issued_at?: string;
  notes?: string;
  has_interaction_warnings?: boolean;
  pharmacy_name?: string;
  created_at?: string;
}

export interface PrescriptionItem {
  id: number;
  prescription?: number;
  medication_name: string;
  dosage?: string;
  frequency?: string;
  duration?: string;
  quantity?: number;
  instructions?: string;
}

export interface PrescriptionsFilters {
  search?: string;
  status?: string;
  page?: number;
  page_size?: number;
}
