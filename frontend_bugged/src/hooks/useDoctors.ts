import { useCallback, useEffect, useStat } from "react";
import { profilesApi } from "../x/api/profiles";

export function useDoctors(params?: Record<string, string>) {
  const [doctors, setDoctors] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const reload = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await profilesApi.list(params);
      setDoctors(data.results ?? []);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load doctors");
      setDoctors([]);
    } finally {
      setLoading(false);
    }
  }, [params]);

  useEffect(() => {
    void reload();
  }, [reload]);

  const loadFeatured = useCallback(async () => {
    try {
      const data = await profilesApi.featured();
      setDoctors(Array.isArray(data) ? data : []);
    } catch {
      setDoctors([]);
    }
  }, []);

  return { doctors, loading, error, reload, loadFeatured };
}
