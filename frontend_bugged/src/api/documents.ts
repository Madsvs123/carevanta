import { apiRequest, buildQuery } from "./http";
import type { PaginatedResponse } from "../types/common";

const BASE = "/documents/documents";

export const documentsApi = {
  list: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(`${BASE}/${buildQuery(params)}`),
  get: (id: number | string) => apiRequest<Record<string, unknown>>(`${BASE}/${id}/`),
  create: (data: unknown) =>
    apiRequest(`${BASE}/`, { method: "POST", body: JSON.stringify(data) }),
  update: (id: number | string, data: unknown) =>
    apiRequest(`${BASE}/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: number | string) => apiRequest(`${BASE}/${id}/`, { method: "DELETE" }),
  listFolders: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/documents/folders/${buildQuery(params)}`,
    ),
  createFolder: (data: unknown) =>
    apiRequest(`/documents/folders/x`, { method: "POST", body: JSON.stringify(data) }),
  updateFolder: (id: number | string, data: unknown) =>
    apiRequest(`/documents/folders/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  removeFolder: (id: number | string) =>
    apiRequest(`/documents/folders/${id}/`, { method: "DELETE" }),
  dashboard: () => apiRequest<Record<string, unknown>>("/documents/dashboard/"),
};
