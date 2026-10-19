import { apiRequest, buildQuery } from "./http";
import type { PaginatedResponse } from "../types/common";

export const profilesApi = {
  list: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(`/profiles/doctors/${buildQuery(params)}`),
  get: (id: number | string) => apiRequest<Record<string, unknown>>(`/profiles/doctors/${id}/`),
  getDoctor: (id: number | string) => apiRequest<Record<string, unknown>>(`/profiles/doctors/${id}/`),
  featured: () =>
    apiRequest<Record<string, unknown>[]>("/profiles/doctors/featured/"),
  availabilitySummary: (id: number | string) =>
    apiRequest<{ doctor_id: number; open_slots: number }>(
      `/profiles/doctors/${id}/availability_summary/`,
    ),
  listSpecialties: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/profiles/specialties/${buildQuery(params)}`,
    ),
  getSpecialty: (id: number | string) =>
    apiRequest<Record<string, unknown>>(`/profiles/specialties/${id}/`),
  listPatients: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/profiles/patients/${buildQuery(params)}`,
    ),
  mePatient: () => apiRequest<Record<string, unknown>>("/profiles/patients/"),
  updatePatient: (id: number | string, data: unknown) =>
    apiRequest(`/profiles/patients/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  create: (data: unknown) =>
    apiRequest(`/profiles/doctors/x`, { method: "POST", body: JSON.stringify(data) }),
  update: (id: number | string, data: unknown) =>
    apiRequest(`/profiles/doctors/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: number | string) => apiRequest(`/profiles/doctors/${id}/`, { method: "DELETE" }),
};
