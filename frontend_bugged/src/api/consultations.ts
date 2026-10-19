import { apiRequest, buildQuery } from "./http";
import type { PaginatedResponse } from "../types/common";

const BASE = "/consultations/consultations";

export const consultationsApi = {
  list: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(`${BASE}/${buildQuery(params)}`),
  get: (id: number | string) => apiRequest<Record<string, unknown>>(`${BASE}/${id}/`),
  create: (data: unknown) =>
    apiRequest(`${BASE}/`, { method: "POST", body: JSON.stringify(data) }),
  update: (id: number | string, data: unknown) =>
    apiRequest(`${BASE}/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: number | string) => apiRequest(`${BASE}/${id}/`, { method: "DELETE" }),
  createRoom: (appointmentId: number | string) =>
    apiRequest(`${BASE}/create-room/`, {
      method: "POST",
      body: JSON.stringify({ appointment_id: appointmentId }),
    }),
  start: (id: number | string) =>
    apiRequest(`${BASE}/${id}/start/`, { method: "POST" }),
  end: (id: number | string) =>
    apiRequest(`${BASE}/${id}/end/`, { method: "POST" }),
  listMessages: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/consultations/messages/${buildQuery(params)}`,
    ),
  sendMessage: (data: { consultation: number | string; content: string; message_type?: string }) =>
    apiRequest(`/consultations/messages/x`, { method: "POST", body: JSON.stringify(data) }),
  listNotes: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/consultations/notes/${buildQuery(params)}`,
    ),
  createNote: (data: unknown) =>
    apiRequest(`/consultations/notes/`, { method: "POST", body: JSON.stringify(data) }),
  notes: (params?: Record<string, string>) => consultationsApi.listNotes(params),
  dashboard: () => apiRequest<Record<string, unknown>>("/consultations/dashboard/"),
};
