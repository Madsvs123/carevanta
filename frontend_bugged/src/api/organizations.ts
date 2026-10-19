import { apiRequest, buildQuery } from "./http";
import type { PaginatedResponse } from "../types/common";

const BASE = "/organizations/clinics";

export const organizationsApi = {
  list: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(`${BASE}/${buildQuery(params)}`),
  get: (id: number | string) => apiRequest<Record<string, unknown>>(`${BASE}/${id}/`),
  create: (data: unknown) =>
    apiRequest(`${BASE}/`, { method: "POST", body: JSON.stringify(data) }),
  update: (id: number | string, data: unknown) =>
    apiRequest(`${BASE}/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: number | string) => apiRequest(`${BASE}/${id}/`, { method: "DELETE" }),
  featured: () => apiRequest<Record<string, unknown>[]>(`${BASE}/featured/`),
  staff: (id: number | string) =>
    apiRequest<Record<string, unknown>[]>(`${BASE}/${id}/staff/`),
  listLocations: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/organizations/locations/${buildQuery(params)}`,
    ),
  listStaff: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/organizations/staff/${buildQuery(params)}`,
    ),
  listInvitations: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/organizations/invitations/${buildQuery(params)}`,
    ),
  createInvitation: (data: unknown) =>
    apiRequest(`/organizations/invitations/`, { method: "POST", body: JSON.stringify(data) }),
  listSettings: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/organizations/settings/${buildQuery(params)}`,
    ),
  updateSettings: (id: number | string, data: unknown) =>
    apiRequest(`/organizations/settings/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  dashboard: () => apiRequest<Record<string, unknown>>("/organizations/dashboard/"),
};
