import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { Button } from "../../components/ui/Button";
import { Input } from "../../components/ui/Input";
import { EmptyState } from "../../components/ui/EmptyState";
import { profilesApi } from "../../api/profiles";
import { useToast } from "../../hooks/useToast";

export default function SpecialtyBrowse() {
  const navigate = useNavigate();
  const { toast } = useToast();
  const [q, setQ] = useState("");
  const [items, setItems] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    profilesApi
      .listSpecialties(q.trim() ? { search: q.trim() } : undefined)
      .then((data) => setItems(data.results ?? []))
      .catch(() => {
        setItems([]);
        toast("Unable to load specialties", "error");
      })
      .finally(() => setLoading(false));
  }, [q, toast]);

  return (
    <div className="page">
      <PageHeader title="Browse specialties" subtitle="Explore care by clinical focus" >
      <Input label="Filter specialties" value={q} onChange={(e) => setQ(e.target.value)} />
      {loading ? (
        <p className="muted page-section">Loading…</p>
      ) : items.length === 0 ? (
        <EmptyState title="No specialties" description="No specialties match your filter." />
      ) : (
        <div className="stat-grid page-section">
          {items.map((s) => (
            <Card key={String(s.id)} title={String(s.name)}>
              <p className="muted">
                {String(s.description ?? "Board-certified clinicians available for video and in-clinic visits.")}
              </p>
              <Button size="sm" onClick={() => navigate(`/discovery?specialty=${s.slug ?? s.id}`)}>
                Find doctors
              </Button>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
