import { createStore, useStore } from "./createStore";
import { workflowsApi, type WorkflowResult } from "../api/workflows";

export type DomainModule =
  | "accounts"
  | "organizations"
  | "profiles"
  | "scheduling"
  | "appointments"
  | "consultations"
  | "medical_records"
  | "prescriptions"
  | "laboratories"
  | "billing"
  | "messaging"
  | "notifications"
  | "documents"
  | "insurance"
  | "support";

type ModuleBucket = {
  loading: boolean;
  error: string | null;
  dashboard: Record<string, unknown> | null;
  lastResult: WorkflowResult | null;
  operations: { name: string; doc: string }[];
};

type PlatformState = {
  modules: Record<DomainModule, ModuleBucket>;
  ui: {
    sidebarCollapsed: boolean;
    lastModule: DomainModule | null;
  };
};

const emptyBucket = (): ModuleBucket => ({
  loading: true,
  error: null,
  dashboard: null,
  lastResult: null,
  operations: [],
});

const MODULES: DomainModule[] = [
  "accounts",
  "organizations",
  "profiles",
  "scheduling",
  "appointments",
  "consultations",
  "medical_records",
  "prescriptions",
  "laboratories",
  "billing",
  "messaging",
  "notifications",
  "documents",
  "insurance",
  "support",
];

function initialModules(): Record<DomainModule, ModuleBucket> {
  return Object.fromEntries(MODULES.map((m) => [m, emptyBucket()])) as Record<
    DomainModule,
    ModuleBucket
  >;
}

export const platformStore = createStore<PlatformState>({
  modules: initialModules(),
  ui: { sidebarCollapsed: false, lastModule: null },
});

function patchModule(module: DomainModule, partial: Partial<ModuleBucket>) {
  const current = platformStore.getState().modules[module];
  platformStore.setState({
    modules: {
      ...platformStore.getState().modules,
      [module]: { ...current, ...partial },
    },
  });
}

export const platformActions = {
  toggleSidebar() {
    const ui = platformStore.getState().ui;
    platformStore.setState({ ui: { ...ui, sidebarCollapsed: !ui.sidebarCollapsed } });
  },

  async loadDashboard(module: DomainModule) {
    patchModule(module, { loading: true, error: null });
    platformStore.setState({
      ui: { ...platformStore.getState().ui, lastModule: module },
    });
    try {
      const [dashboard, described] = await Promise.all([
        workflowsApi.dashboard(module),
        workflowsApi.describe(module).catch(() => ({ operations: [] as { name: string; doc: string }[] })),
      ]);
      patchModule(module, {
        loading: false,
        dashboard,
        operations: described.operations ?? [],
      });
    } catch (e) {
      patchModule(module, {
        loading: false,
        error: e instanceof Error ? e.message : "Failed to load dashboard",
      });
    }
  },

  async runWorkflow(module: DomainModule, operation: string, payload: Record<string, unknown> = {}) {
    patchModule(module, { loading: true, error: null });
    try {
      const result = await workflowsApi.run(module, operation, payload);
      patchModule(module, { loading: false, lastResult: result });
      return result;
    } catch (e) {
      const message = e instanceof Error ? e.message : "Workflow failed";
      patchModule(module, { loading: false, error: message });
      throw e;
    }
  },

  clearError(module: DomainModule) {
    patchModule(module, { error: null });
  },
};

export function usePlatformModule(module: DomainModule) {
  return useStore(platformStore, (s) => s.modules[module]);
}

export function usePlatformUi() {
  return useStore(platformStore, (s) => s.ui);
}

export { MODULES };
