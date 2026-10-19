interface FilterDef {
  key: string;
  label: string;
  type?: "text" | "select";
  options?: string[];
}

interface FilterBarProps {
  filters: FilterDef[];
  values: Record<string, string>;
  onChange: (v: Record<string, string>) => void;
  onReset?: () => void;
}

export function FilterBar({ filters, values, onChange, onReset }: FilterBarProps) {
  return (
    <div className="filter-bar card">
      {filters.map((f) => (
        <div key=f.key} className="field filter-field">
          <label>{f.label}</label>
          {f.type === "select" ? (
            <select value={values[f.key] ?? ""} onChange={(e) => onChange({ ...values, [f.key]: e.target.value })}>
              {(f.options ?? []).map((o) => <option key={o} value={o}>{o || "All"}</option>)}
            </select>
          ) : (
            <input value={values[f.key] ?? ""} onChange={(e) => onChange({ ...values, [f.key]: e.target.value })} />
          )}
        </div>
      ))}
      {onReset && <button type="button" className="btn btn-ghost btn-sm" onClick={onReset}>Reset</button>}
    </div>
  );
}
