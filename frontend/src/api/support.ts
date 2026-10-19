import { apiRequest, buildQuery } from "./http";
import type { PaginatedResponse } from "../types/common";

const BASE = "/support/tickets";

export const supportApi = {
  list: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(`${BASE}/${buildQuery(params)}`),
  get: (id: number | string) => apiRequest<Record<string, unknown>>(`${BASE}/${id}/`),
  create: (data: unknown) =>
    apiRequest(`${BASE}/`, { method: "POST", body: JSON.stringify(data) }),
  update: (id: number | string, data: unknown) =>
    apiRequest(`${BASE}/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: number | string) => apiRequest(`${BASE}/${id}/`, { method: "DELETE" }),
  close: (id: number | string) =>
    apiRequest(`${BASE}/${id}/close/`, { method: "POST" }),
  reopen: (id: number | string) =>
    apiRequest(`${BASE}/${id}/reopen/`, { method: "POST" }),
  assign: (id: number | string, assigneeId: number | string) =>
    apiRequest(`${BASE}/${id}/assign/`, {
      method: "POST",
      body: JSON.stringify({ assignee_id: assigneeId }),
    }),
  listMessages: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/support/ticket-messages/${buildQuery(params)}`,
    ),
  createMessage: (data: unknown) =>
    apiRequest(`/support/ticket-messages/`, { method: "POST", body: JSON.stringify(data) }),
  listAttachments: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/support/ticket-attachments/${buildQuery(params)}`,
    ),
  dashboard: () => apiRequest<Record<string, unknown>>("/support/dashboard/"),
};
