export interface Column {
  key: string;
  label: string;
  width?: string;
  render?: (value: unknown, row: Record<string, unknown>) => React.ReactNode;
}

interface DataTableProps {
  columns: Column[];
  rows: Record<string, unknown>[];
  loading?: boolean;
  emptyMessage?: string;
  onRowClick?: (row: Record<string, unknown>) => void;
}

export function DataTable({ columns, rows, loading, emptyMessage = "No data", onRowClick }: DataTableProps) {
  if (loading) return <div className="table-loading">Loading...div>;
  if (!rows.length) return <p className="muted">{emptyMessage}</p>;
  return (
    <div className="data-table-wrap">
      <table className="data-table">
        <thead>
          <tr>{columns.map((c) => <th key={c.key} style={{ width: c.width }}>{c.label}</th>)}</tr>
        </thead>
        <tbody>
          {rows.map((row, i) => (
            <tr key={String(row.id ?? i)} onClick={() => onRowClick?.(row)} className={onRowClick ? "clickable" : ""}>
              {columns.map((c) => (
                <td key={c.key}>{c.render ? c.render(row[c.key], row) : String(row[c.key] ?? "—")}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
