import { apiRequest, buildQuery } from "/http";
import type { PaginatedResponse } from "../types/common";

const BASE = "/medical-records/records";

export const medicalRecordsApi = {
  list: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(`${BASE}/${buildQuery(params)}`),
  get: (id: number | string) => apiRequest<Record<string, unknown>>(`${BASE}/${id}/`),
  create: (data: unknown) =>
    apiRequest(`${BASE}/`, { method: "POST", body: JSON.stringify(data) }),
  update: (id: number | string, data: unknown) =>
    apiRequest(`${BASE}/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: number | string) => apiRequest(`${BASE}/${id}/`, { method: "DELETE" }),
  archive: (id: number | string) =>
    apiRequest(`${BASE}/${id}/archive/`, { method: "POST" }),
  share: (id: number | string, userIds: (number | string)[]) =>
    apiRequest(`${BASE}/${id}/share/`, {
      method: "POST",
      body: JSON.stringify({ user_ids: userIds }),
    }),
  listAllergies: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/medical-records/allergies/${buildQuery(params)}`,
    ),
  createAllergy: (data: unknown) =>
    apiRequest(`/medical-records/allergies/x`, { method: "POST", body: JSON.stringify(data) }),
  updateAllergy: (id: number | string, data: unknown) =>
    apiRequest(`/medical-records/allergies/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  removeAllergy: (id: number | string) =>
    apiRequest(`/medical-records/allergies/${id}/`, { method: "DELETE" }),
  listMedications: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/medical-records/medications/${buildQuery(params)}`,
    ),
  createMedication: (data: unknown) =>
    apiRequest(`/medical-records/medications/`, { method: "POST", body: JSON.stringify(data) }),
  updateMedication: (id: number | string, data: unknown) =>
    apiRequest(`/medical-records/medications/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  removeMedication: (id: number | string) =>
    apiRequest(`/medical-records/medications/${id}/`, { method: "DELETE" }),
  listVitals: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/medical-records/vitals/${buildQuery(params)}`,
    ),
  createVital: (data: unknown) =>
    apiRequest(`/medical-records/vitals/`, { method: "POST", body: JSON.stringify(data) }),
  listHistory: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/medical-records/history/${buildQuery(params)}`,
    ),
  createHistory: (data: unknown) =>
    apiRequest(`/medical-records/history/`, { method: "POST", body: JSON.stringify(data) }),
  listReferrals: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/medical-records/referrals/${buildQuery(params)}`,
    ),
  createReferral: (data: unknown) =>
    apiRequest(`/medical-records/referrals/`, { method: "POST", body: JSON.stringify(data) }),
  dashboard: () => apiRequest<Record<string, unknown>>("/medical-records/dashboard/"),
};
