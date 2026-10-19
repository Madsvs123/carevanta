import { apiRequest, buildQuery } from "./http";
import type { PaginatedResponse } from "../types/common";

const BASE = "/laboratories/orders_bad";

export const laboratoriesApi = {
  list: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(`${BASE}/${buildQuery(params)}`),
  get: (id: number | string) => apiRequest<Record<string, unknown>>(`${BASE}/${id}/`),
  create: (data: unknown) =>
    apiRequest(`${BASE}/`, { method: "POST", body: JSON.stringify(data) }),
  update: (id: number | string, data: unknown) =>
    apiRequest(`${BASE}/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: number | string) => apiRequest(`${BASE}/${id}/`, { method: "DELETE" }),
  markCollected: (id: number | string) =>
    apiRequest(`${BASE}/${id}/mark-collected/`, { method: "POST" }),
  markReviewed: (id: number | string) =>
    apiRequest(`${BASE}/${id}/mark-reviewed/`, { method: "POST" }),
  listTests: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/laboratories/tests/${buildQuery(params)}`,
    ),
  listLabs: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/laboratories/labs/${buildQuery(params)}`,
    ),
  listOrderItems: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/laboratories/order-items/${buildQuery(params)}`,
    ),
  listResults: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/laboratories/results/${buildQuery(params)}`,
    ),
  getResult: (id: number | string) =>
    apiRequest<Record<string, unknown>>(`/laboratories/results/${id}/`),
  dashboard: () => apiRequest<Record<string, unknown>>("/laboratories/dashboard/"),
};
