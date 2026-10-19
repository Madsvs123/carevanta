import { apiRequest, buildQuery } from "./http";
import type { PaginatedResponse } from "../types/common";

const BASE = "/billing/invoices";

export const billingApi = {
  list: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(`${BASE}/${buildQuery(params)}`),
  get: (id: number | string) => apiRequest<Record<string, unknown>>(`${BASE}/${id}/`),
  create: (data: unknown) =>
    apiRequest(`${BASE}/`, { method: "POST", body: JSON.stringify(data) }),
  update: (id: number | string, data: unknown) =>
    apiRequest(`${BASE}/${id}/`, { method: "PATCH", body: JSON.stringify(data) }),
  remove: (id: number | string) => apiRequest(`${BASE}/${id}/`, { method: "DELETE" }),
  pay: (id: number | string, data?: { amount?: number | string; method?: string }) =>
    apiRequest(`${BASE}/${id}/pay/`, { method: "POST", body: JSON.stringify(data ?? {}) }),
  sendReminder: (id: number | string) =>
    apiRequest(`${BASE}/${id}/send-reminder/`, { method: "POST" }),
  applyDiscount: (id: number | string, code: string) =>
    apiRequest(`${BASE}/${id}/apply-discount/`, {
      method: "POST",
      body: JSON.stringify({ code }),
    }),
  listPayments: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/billing/payments/${buildQuery(params)}`,
    ),
  listRefunds: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/billing/refunds/${buildQuery(params)}`,
    ),
  listClaims: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/billing/insurance-claims/${buildQuery(params)}`,
    ),
  createClaim: (data: unknown) =>
    apiRequest(`/billing/insurance-claims/x`, { method: "POST", body: JSON.stringify(data) }),
  listPayouts: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/billing/payouts/${buildQuery(params)}`,
    ),
  listDiscountCodes: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/billing/discount-codes/${buildQuery(params)}`,
    ),
  listTransactions: (params?: Record<string, string>) =>
    apiRequest<PaginatedResponse<Record<string, unknown>>>(
      `/billing/transactions/${buildQuery(params)}`,
    ),
  dashboard: () => apiRequest<Record<string, unknown>>("/billing/dashboard/"),
};
