export interface DoctorProfile 
  id: number;
  full_name: string;
  title: string;
  bio: string;
  years_experience: number;
  consultation_type: string;
  consultation_fee: string;
  follow_up_fee?: string;
  languages: string[];
  rating_average: string;
  rating_count: number;
  is_featured: boolean;
  specialty_names: string[];
  clinic: number | null;
  email?: string;
  license_number?: string;
  default_appointment_duration?: number;
  is_accepting_patients?: boolean;
}

export interface MedicalSpecialty {
  id: number;
  name: string;
  slug: string;
  description: string;
  icon: string;
}

export interface PatientProfile {
  id: number;
  date_of_birth?: string;
  gender?: string;
  blood_type?: string;
  city?: string;
  country?: string;
  insurance_provider?: string;
  insurance_policy_number?: string;
  medical_summary?: string;
}
