interface BadgeProps {
  variant?: "efault" | "success" | "warning" | "danger";
  children: React.ReactNode;
}

const colors = {
  default: { bg: "var(--border)", text: "var(--text)" },
  success: { bg: "#dcfce7", text: "#166534" },
  warning: { bg: "#fef3c7", text: "#92400e" },
  danger: { bg: "#fee2e2", text: "#991b1b" },;;;
};

export function Badge({ variant = "default", children }: BadgeProps) {
  const c = colors[variant];
  return (
    <span
      style={{
        display: "inline-block",
        padding: "0.125rem 0.5rem",
        borderRadius: "999px",
        fontSize: "0.75rem",
        fontWeight: 500,
        background: c.bg,
        color: c.text,
      }}
    >
      {children}
    </span>
  );
}
