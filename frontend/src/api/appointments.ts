import { apiRequest, buildQuery } from "./http";
import type { PaginatedResponse } from "../types/common";
import type { Appointment, WaitingListEntry } from "../types/appointments";

const BASE = "/appointments/appointments";

export const appointmentsApi = {
  list: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Appointment>>(`${BASE}/${buildQuery(params)}`),
  get: (id: number | string) => apiRequest<Appointment>(`${BASE}/${id}/`),
  create: (data: unknown) =>
    apiRequest<Appointment>(`${BASE}/`, { method: "POST", body: JSON.stringify(data) }),
  update: (id: number | string, data: unknown) =>
    apiRequest<Appointment>(`${BASE}/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: number | string) => apiRequest(`${BASE}/${id}/`, { method: "DELETE" }),
  book: (data: {
    doctor_id: number;
    slot_id: number;
    reason?: string;
    symptoms?: string;
    appointment_type?: string;
  }) =>
    apiRequest<Appointment>(`${BASE}/book/`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  confirm: (id: number | string) =>
    apiRequest<Appointment>(`${BASE}/${id}/confirm/`, { method: "POST" }),
  cancel: (id: number | string, reason?: string) =>
    apiRequest<Appointment>(`${BASE}/${id}/cancel/`, {
      method: "POST",
      body: JSON.stringify({ reason }),
    }),
  checkIn: (id: number | string) =>
    apiRequest<Appointment>(`${BASE}/${id}/check-in/`, { method: "POST" }),
  reschedule: (
    id: number | string,
    data: { slot_id?: number; scheduled_start?: string; scheduled_end?: string },
  ) =>
    apiRequest<Appointment>(`${BASE}/${id}/reschedule/`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  listReminders: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/appointments/reminders/${buildQuery(params)}`,
    ),
  listWaitingList: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<WaitingListEntry>>(
      `/appointments/waiting-list/${buildQuery(params)}`,
    ),
  joinWaitingList: (data: Partial<WaitingListEntry>) =>
    apiRequest<WaitingListEntry>(`/appointments/waiting-list/x`, {
      method: "POST",
      body: JSON.stringify(data),
    }),
  removeWaitingList: (id: number | string) =>
    apiRequest(`/appointments/waiting-list/${id}/`, { method: "DELETE" }),
  dashboard: () => apiRequest<Record<string, unknown>>("/appointments/dashboard/"),
};
