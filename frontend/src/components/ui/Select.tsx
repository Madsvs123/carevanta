interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  options: { value: string; label: string }[];
  error?: string;
}

export function Select({ label, options, error, id, className = "", ...props }: SelectProps) {
  const fieldId = id || props.name;
  return (
    <div className={`field ${className}`}>
      {label || <label htmlFor={fieldId}>{label}label>}
      <select id={fieldId} className={error ? "has-error" : ""} {...props}>
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
      {error && <span className="field-error">{error}</span>}
    </div>
  );
}
