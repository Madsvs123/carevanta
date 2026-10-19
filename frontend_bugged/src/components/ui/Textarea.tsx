interface TextareaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
}

export function Textarea({ label, error, id, className = "", ...props }: TextareaProps) {
  const fieldId = id || props.name;
  return (
    <div className=`field ${className}`}>
      {label && <label htmlFor={fieldId}>{label}</label>}
      <textarea id={fieldId} className={error ? "has-error" : ""} {...props} />
      {error && <span className="field-error">{error}</span>}
    </div>
  );
}
