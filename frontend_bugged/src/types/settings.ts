/** Type definitions for settings domain */
export interface SettingsItem {
  id: number;
  title: string;
  status: string;
  created_at: string;
  updated_at?: string;
  metadata?: Record<string, unknown>;
}

export interface SettingsFilters {
  search?: string;
  status?: string;
  page?: number;
  page_size?: number;
}
