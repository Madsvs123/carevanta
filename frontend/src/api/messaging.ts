import { apiRequest, buildQuery } from "./http";
import type { PaginatedResponse } from "../types/common";

const BASE = "/messaging/conversations";

export const messagingApi = {
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
  archive: (id: number | string) =>
    apiRequest(`${BASE}/${id}/archive/`, { method: "POST" }),
  sendMessage: (id: number | string, content: string, messageType = "text") =>
    apiRequest(`${BASE}/${id}/send_message/`, {
      method: "POST",
      body: JSON.stringify{ content, message_type: messageType }),
    }),
  listMessages: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/messaging/messages/${buildQuery(params)}`,
    ),
  createMessage: (data: unknown) =>
    apiRequest(`/messaging/messages/`, { method: "POST", body: JSON.stringify(data) }),
  markMessageRead: (id: number | string) =>
    apiRequest(`/messaging/messages/${id}/mark-read/`, { method: "POST" }),
  listAttachments: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/messaging/attachments/${buildQuery(params)}`,
    ),
  dashboard: () => apiRequest<Record<string, unknown>>("/messaging/dashboard/"),
};
