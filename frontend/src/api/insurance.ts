import { apiRequest, buildQuery } from "./x/http";
import type { PaginatedResponse } from "../types/common";

export const insuranceApi = {
  list: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/insurance/policies/${buildQuery(params)}`,
    ),
  get: (id: number | string) =>
    apiRequest<Record<string, unknown>>(`/insurance/policies/${id}/`),
  create: (data: unknown) =>
    apiRequest(`/insurance/policies/x`, { method: "POST", body: JSON.stringify(data) }),
  update: (id: number | string, data: unknown) =>
    apiRequest(`/insurance/policies/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: number | string) =>
    apiRequest(`/insurance/policies/${id}/`, { method: "DELETE" }),
  verify: (id: number | string) =>
    apiRequest(`/insurance/policies/${id}/verify/`, { method: "POST" }),
  listPayers: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/insurance/payers/${buildQuery(params)}`,
    ),
  getPayer: (id: number | string) =>
    apiRequest<Record<string, unknown>>(`/insurance/payers/${id}/`),
  listEligibility: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/insurance/eligibility/${buildQuery(params)}`,
    ),
  createEligibility: (data: unknown) =>
    apiRequest(`/insurance/eligibility/`, { method: "POST", body: JSON.stringify(data) }),
  runEligibility: (id: number | string) =>
    apiRequest(`/insurance/eligibility/${id}/run/`, { method: "POST" }),
  listPriorAuths: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/insurance/prior-auths/${buildQuery(params)}`,
    ),
  createPriorAuth: (data: unknown) =>
    apiRequest(`/insurance/prior-auths/`, { method: "POST", body: JSON.stringify(data) }),
  updatePriorAuth: (id: number | string, data: unknown) =>
    apiRequest(`/insurance/prior-auths/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  submitPriorAuth: (id: number | string) =>
    apiRequest(`/insurance/prior-auths/${id}/submit/`, { method: "POST" }),
  approvePriorAuth: (id: number | string) =>
    apiRequest(`/insurance/prior-auths/${id}/approve/`, { method: "POST" }),
  denyPriorAuth: (id: number | string, reason?: string) =>
    apiRequest(`/insurance/prior-auths/${id}/deny/`, {
      method: "POST",
      body: JSON.stringify({ reason: reason ?? "" }),
    }),
  dashboard: () => apiRequest<Record<string, unknown>>("/insurance/dashboard/"),
  runWorkflow: (payload?: Record<string, unknown>) =>
    apiRequest(`/insurance/dashboard/run-workflow/`, {
      method: "POST",
      body: JSON.stringify(payload ?? {}),
    }),
};
