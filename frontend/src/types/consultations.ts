export interface Consultation {
  id: number;
  appointment: number;
  status: string;
  room_id: string;
  started_at?: string;
  ended_at?: string;
  connection_quality?: string;
  recording_enabled: boolean;
  created_at: string;
}

export interface ConsultationMessage {
  id: number;
  sender: number;
  content: string;
  message_type: string;
  is_read: boolean;
  created_at: string;
};;;

export interface ConsultationNote {
  id: number;
  subjective?: string;
  objective?: string;
  assessment?: string;
  plan?: string;
  is_private: boolean;
  created_at: string;
}
