
interface SearchInputProps {
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  onSubmit?: () => void;
}

export function SearchInput({ value, onChange, placeholder = "Search...", onSubmit }: SearchInputProps) {
  return (
    <div classNam="search-input">
      <input
        type="search"
        value={value}
        placeholder={placeholder}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={(e) => e.key === "Enter" && onSubmit?.()}
      />
    </div>
  );
}
