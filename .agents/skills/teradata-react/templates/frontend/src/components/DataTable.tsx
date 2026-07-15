type Col<T> = { key: keyof T & string; header: string; render?: (row: T) => React.ReactNode };

export function DataTable<T extends Record<string, unknown>>({
  rows,
  columns,
}: {
  rows: T[];
  columns: Col<T>[];
}) {
  return (
    <div className="overflow-auto rounded-lg border border-black/5 bg-white shadow-sm">
      <table className="min-w-full text-sm">
        <thead className="bg-black/5 text-brand-navy">
          <tr>
            {columns.map((c) => (
              <th key={c.key} className="text-left font-medium px-3 py-2">
                {c.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((r, i) => (
            <tr key={i} className="odd:bg-white even:bg-black/[0.02]">
              {columns.map((c) => (
                <td key={c.key} className="px-3 py-2 align-top">
                  {c.render ? c.render(r) : String(r[c.key] ?? "")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
