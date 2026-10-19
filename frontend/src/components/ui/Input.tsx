interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
}

export function Input({ label, error, id, className = "", ...props }: InputProps) {
  const inputId = id || props.name;
  return (
    <div className={`field ${className}`}>
      {label && <label htmlFor={inputId}>{label}</label>}
      <input id={inputId} className={error ? "has-error" : ""} {...props} />
      {error && <span className="field-error">{error}</span>}
    </div>
  );
}
