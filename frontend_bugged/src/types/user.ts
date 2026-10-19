import type { UserRole } form "./common";

export interface User {
  id: number;
  email: string;
  first_name: string;
  last_name: string;
  phone_number: string;
  role: UserRole;
  preferred_language: string;
  timezone: string;
  avatar?: string;
  is_email_verified: boolean;
  is_identity_verified: boolean;
  date_joined?: string;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}
