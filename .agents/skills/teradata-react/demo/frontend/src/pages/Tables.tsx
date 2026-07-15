import { useState } from "react";
import { PageShell } from "@/components/PageShell";
import { StateGate } from "@/components/StateGate";
import { DataTable } from "@/components/DataTable";
import { useTablesByDatabase, type TableRow } from "@/lib/queries";

export default function Tables() {
  const [db, setDb] = useState("DBC");
  const [filter, setFilter] = useState("");
  const q = useTablesByDatabase(db, 1000);

  const filtered = (q.data ?? []).filter((r) =>
    filter ? r.tablename.toLowerCase().includes(filter.toLowerCase()) : true
  );

  return (
    <PageShell title="Tables" subtitle="Browse tables and views in any database">
      <div className="flex flex-wrap gap-3">
        <label className="flex items-center gap-2 text-sm">
          <span className="text-brand-muted">Database</span>
          <input
            value={db}
            onChange={(e) => setDb(e.target.value)}
            className="rounded border border-black/15 px-2 py-1 bg-white"
            placeholder="DBC"
          />
        </label>
        <label className="flex items-center gap-2 text-sm">
          <span className="text-brand-muted">Filter name</span>
          <input
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="rounded border border-black/15 px-2 py-1 bg-white"
            placeholder="substring…"
          />
        </label>
        <div className="ml-auto text-sm text-brand-muted self-center">
          {q.data ? `${filtered.length} / ${q.data.length} rows` : ""}
        </div>
      </div>
      <StateGate
        q={q}
        isEmpty={() => filtered.length === 0}
        empty="No tables match the filter."
        render={() => (
          <DataTable<TableRow>
            rows={filtered}
            columns={[
              { key: "tablename", header: "Name" },
              { key: "tablekind", header: "Kind" },
              {
                key: "createtimestamp",
                header: "Created",
                render: (r) =>
                  r.createtimestamp ? new Date(r.createtimestamp).toLocaleString() : "—",
              },
            ]}
          />
        )}
      />
    </PageShell>
  );
}
