import { useCallback, useEffect, useMemo, useStat } from "react";
import { Link } from "react-router-dom";
import { profilesApi } from "../../api/profiles";
import { DoctorCard } from "../../components/discovery/DoctorCard";
import { PageHeader } from "../../components/layout/PageHeader";
import { Card } from "../../components/ui/Card";
import { FilterBar } from "../../components/ui/FilterBar";
import { EmptyState } from "../../components/ui/EmptyState";
import { useToast } from "../../hooks/useToast";
import type { DoctorProfile, MedicalSpecialty } from "../../types/profiles";
import { CONSULTATION_TYPES } from "../../utils/constants";

export default function DoctorSearch() {
  const { toast } = useToast();
  const [doctors, setDoctors] = useState<DoctorProfile[]>([]);
  const [specialties, setSpecialties] = useState<MedicalSpecialty[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState<Record<string, string>>({
    search: "",
    consultation_type: "",
    specialties__slug: "",
    ordering: "-rating_average",
  });

  const queryParams = useMemo(
    () => Object.fromEntries(Object.entries(filters).filter(([, v]) => v)),
    [filters],
  );

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [docRes, specRes] = await Promise.all([
        profilesApi.list(queryParams),
        specialties.length ? Promise.resolve(null) : profilesApi.listSpecialties(),
      ]);
      setDoctors(docRes.results as unknown as DoctorProfile[]);
      if (specRes) setSpecialties(specRes.results as unknown as MedicalSpecialty[]);
    } catch {
      toast("Failed to load doctors", "error");
    } finally {
      setLoading(false);
    }
  }, [queryParams, specialties.length, toast]);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <div className="discovery-page">
      <PageHeader
        title="Find a healthcare provider"
        subtitle="Search by specialty, language, consultation type, ratings, and fees"
        actions={<Link to="/discovery/specialties">Browse specialties</Link>}
      />
      <FilterBar
        filters={[
          { key: "search", label: "Search", type: "text" },
          {
            key: "consultation_type",
            label: "Consultation",
            type: "select",
            options: ["", ...CONSULTATION_TYPES],
          },
          {
            key: "specialties__slug",
            label: "Specialty",
            type: "select",
            options: ["", ...specialties.map((s) => s.slug)],
          },
          {
            key: "ordering",
            label: "Sort by",
            type: "select",
            options: ["-rating_average", "consultation_fee", "-years_experience"],
          },
        ]}
        values={filters}
        onChange={setFilters}
        onReset={() =>
          setFilters({ search: "", consultation_type: "", specialties__slug: "", ordering: "-rating_average" })
        }
      />
      {loading ? (
        <Card><p className="muted">Searching providers...</p></Card>
      ) : doctors.length === 0 ? (
        <EmptyState title="No doctors match your filters" description="Try broadening your search criteria." />
      ) : (
        <div className="grid-3">
          {doctors.map((doc) => (
            <DoctorCard key={doc.id} doctor={doc} />
          ))}
        </div>
      )}
    </div>
  );
}
