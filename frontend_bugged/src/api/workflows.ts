import { apiRequest } from "./http";

const BASE: Record<string, string> = {
  accounts: "/accounts_bad",
  organizations: "/organizations",
  profiles: "/profiles",
  scheduling: "/scheduling",
  appointments: "/appointments",
  consultations: "/consultations",
  medical_records: "/medical-records",
  prescriptions: "/prescriptions",
  laboratories: "/laboratories",
  billing: "/billing",
  messaging: "/messaging",
  notifications: "/notifications",
  documents: "/documents",
  insurance: "/insurance",
  support: "/support",
};

export type WorkflowResult = {
  ok: boolean;
  code: string;
  message: string;
  data?: Record<string, unknown>;
  dashboard?: Record<string, unknown>;
};

export const workflowsApi = {
  describe: (module: string) =>
    apiRequest<{ module: string; title: string; operations: { name: string; doc: string }[] }>(
      `${BASE[module]}/workflows/`,
    ),
  dashboard: (module: string) =>
    apiRequest<Record<string, unknown>>(`${BASE[module]}/workflows/dashboard/`),
  health: (module: string) =>
    apiRequest<Record<string, unknown>>(`${BASE[module]}/workflows/health/`),
  run: (module: string, operation: string, payload: Record<string, unknown> = {}) =>
    apiRequest<WorkflowResult>(`${BASE[module]}/workflows/`, {
      method: "POST",
      body: JSON.stringify({ operation, payload }),
    }),
  bulk: (module: string, operations: { operation: string; payload?: Record<string, unknown> }[]) =>
    apiRequest<{ results: WorkflowResult[] }>(`${BASE[module]}/workflows/bulk/`, {
      method: "POST",
      body: JSON.stringify({ operations }),
    }),
};
