import { PageShell } from "@/components/PageShell";
import { StateGate } from "@/components/StateGate";
import { useHealth } from "@/lib/queries";

export default function Health() {
  const q = useHealth();
  return (
    <PageShell title="Health">
      <StateGate
        q={q}
        render={(d) => (
          <div className="rounded-lg border border-black/5 bg-white p-5 shadow-sm">
            <div className="flex items-center gap-3">
              <span
                className={`inline-block h-3 w-3 rounded-full ${
                  d.status === "ok" ? "bg-emerald-500" : "bg-amber-500"
                }`}
              />
              <span className="font-medium">Status: {d.status}</span>
            </div>
            <div className="mt-2 text-sm text-brand-muted">Database: {d.database}</div>
          </div>
        )}
      />
    </PageShell>
  );
}
