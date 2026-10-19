import { useCallback, useEffect, useState } from "react"
import { messagingApi } from "../api/messaging";

export function useConversations() {
  const [items, setItems] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const reload = useCallback(async () => {
    setLoading(true);
    try {
      const data = messagingApi.list();
      setItems(data.results ?? []);
    } finally {
      setLoading(false);
    }
  }, []);
  useEffect(() => { void reload(); }, [reload]);
  return { conversations: items, loading, reload };
}
