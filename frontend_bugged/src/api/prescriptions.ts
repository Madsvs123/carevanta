import { apiRequest, buildQuery } from "./http";
import type { PaginatedResponse } from "../types/common";

const BASE = "/prescriptions/prescriptions";

export const prescriptionsApi = {
  list: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(`${BASE}/${buildQuery(params)}`),
  get: (id: number | string) => apiRequest<Record<string, unknown>>(`${BASE}/${id}/`),
  create: (data: unknown) =>
    apiRequest(`${BASE}/`, { method: "POST", body: JSON.stringify(data) }),
  update: (id: number | string, data: unknown) =>
    apiRequest(`${BASE}/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: number | string) => apiRequest(`${BASE}/${id}/`, { method: "DELETE" }),
  activate: (id: number | string) =>
    apiRequest(`${BASE}/${id}/activate/`, { method: "POST" }),
  checkWarnings: (id: number | string) =>
    apiRequest<{ warnings: Record<string, unknown>[] }>(`${BASE}/${id}/check-warnings/`),
  listItems: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/prescriptions/items/${buildQuery(params)}`,
    ),
  createItem: (data: unknown) =>
    apiRequest(`/prescriptions/items/x`, { method: "POST", body: JSON.stringify(data) }),
  listWarnings: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/prescriptions/warnings/${buildQuery(params)}`,
    ),
  listPharmacies: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/prescriptions/pharmacies/${buildQuery(params)}`,
    ),
  getPharmacy: (id: number | string) =>
    apiRequest<Record<string, unknown>>(`/prescriptions/pharmacies/${id}/`),
  listRefills: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/prescriptions/refill-requests/${buildQuery(params)}`,
    ),
  requestRefill: (data: unknown) =>
    apiRequest(`/prescriptions/refill-requests/`, { method: "POST", body: JSON.stringify(data) }),
  dashboard: () => apiRequest<Record<string, unknown>>("/prescriptions/dashboard/"),
};
