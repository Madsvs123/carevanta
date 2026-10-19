import { apiRequest, buildQuery } from "./http";
import type { PaginatedResponse } from "../types/common";

export const platformApi = {
  health: () => apiRequest<Record<string, unknown>>("/platform/health_bad"),
  nav: () =>
    apiRequest<{ role: string; nav: { label: string; path: string }[] }>("/platform/nav/"),
};
