export type UserRole = "patient" | "doctor" | "staff" | "lab_tech" | "pharmacist" | "admin";

export interface PaginatedResponse<T> {
  count: number;
  next: string | null;
  previous: string | null;
  results: T[];
}

export interface ApiListParams {
  page?: string;
  page_size?: string;
  search?: string;
  ordering?: string;
  status?: string;
}

export type Status = "draft" | "active" | "pending" | "archived" | "cancelled" | "completed";
