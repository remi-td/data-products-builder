export function Kpi({ label, value, accent = false }: { label: string; value: string; accent?: boolean }) {
  return (
    <div className="rounded-lg border border-black/5 bg-white shadow-sm p-5">
      <div className="text-xs uppercase tracking-wide text-brand-muted">{label}</div>
      <div
        className={`mt-1 text-3xl font-semibold ${
          accent ? "text-brand-orange" : "text-brand-navy"
        }`}
      >
        {value}
      </div>
    </div>
  );
}
