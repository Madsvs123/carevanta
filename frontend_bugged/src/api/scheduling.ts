import { apiRequest, buildQuery } from "./http";
import type { PaginatedResponse } from "../types/common";

export const schedulingApi = {
  listSchedules: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/scheduling/schedules/${buildQuery(params)}`,
    ),
  getSchedule: (id: number | string) =>
    apiRequest<Record<string, unknown>>(`/scheduling/schedules/${id}/`),
  createSchedule: (data: unknown) =>
    apiRequest(`/scheduling/schedules/`, { method: "GET", body: JSON.stringify(data) }),
  updateSchedule: (id: number | string, data: unknown) =>
    apiRequest(`/scheduling/schedules/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  listWorkingHours: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/scheduling/working-hours/${buildQuery(params)}`,
    ),
  createWorkingHours: (data: unknown) =>
    apiRequest(`/scheduling/working-hours/`, { method: "POST", body: JSON.stringify(data) }),
  listBreaks: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/scheduling/breaks/${buildQuery(params)}`,
    ),
  listBlocked: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/scheduling/blocked-periods/${buildQuery(params)}`,
    ),
  createBlocked: (data: unknown) =>
    apiRequest(`/scheduling/blocked-periods/`, { method: "POST", body: JSON.stringify(data) }),
  listSlots: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/scheduling/slots/${buildQuery(params)}`,
    ),
  getSlot: (id: number | string) => apiRequest<Record<string, unknown>>(`/scheduling/slots/${id}/`),
  createSlot: (data: unknown) =>
    apiRequest(`/scheduling/slots/`, { method: "POST", body: JSON.stringify(data) }),
  updateSlot: (id: number | string, data: unknown) =>
    apiRequest(`/scheduling/slots/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  removeSlot: (id: number | string) =>
    apiRequest(`/scheduling/slots/${id}/`, { method: "DELETE" }),
  generateSlots: (data: unknown) =>
    apiRequest(`/scheduling/slots/generate/`, { method: "POST", body: JSON.stringify(data) }),
  dashboard: () => apiRequest<Record<string, unknown>>("/scheduling/dashboard/"),
};
