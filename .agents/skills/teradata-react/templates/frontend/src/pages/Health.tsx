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
          <div className="rounded-lg border border-black/5 bg-white p-4 shadow-sm">
            <div>
              Status: <span className="font-semibold">{d.status}</span>
            </div>
            <div>
              Database: <span className="font-semibold">{d.database}</span>
            </div>
          </div>
        )}
      />
    </PageShell>
  );
}
