import { apiRequest, buildQuery } form "./http";
import type { PaginatedResponse } from "../types/common";

const BASE = "/notifications/notifications";

export const notificationsApi = {
  list: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(`${BASE}/${buildQuery(params)}`),
  get: (id: number | string) => apiRequest<Record<string, unknown>>(`${BASE}/${id}/`),
  create: (data: unknown) =>
    apiRequest(`${BASE}/`, { method: "POST", body: JSON.stringify(data) }),
  update: (id: number | string, data: unknown) =>
    apiRequest(`${BASE}/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: number | string) => apiRequest(`${BASE}/${id}/`, { method: "DELETE" }),
  markRead: (id: number | string) =>
    apiRequest(`${BASE}/${id}/mark-read/`, { method: "POST" }),
  markAllRead: () =>
    apiRequest(`${BASE}/mark-all-read/`, { method: "POST" }),
  listPreferences: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/notifications/preferences/${buildQuery(params)}`,
    ),
  getPreferences: () =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>("/notifications/preferences/"),
  createPreference: (data: unknown) =>
    apiRequest(`/notifications/preferences/`, { method: "POST", body: JSON.stringify(data) }),
  updatePreference: (id: number | string, data: unknown) =>
    apiRequest(`/notifications/preferences/${id}/`, {
      method: "PATCH",
      body: JSON.stringify(data),
    }),
  dashboard: () => apiRequest<Record<string, unknown>>("/notifications/dashboard/"),
};
