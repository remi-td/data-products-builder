import { NavLink } from "react-router-dom";

const links = [
  { to: "/",          label: "Overview" },
  { to: "/databases", label: "Databases" },
  { to: "/tables",    label: "Tables" },
  { to: "/users",     label: "Users" },
  { to: "/space",     label: "Disk Space" },
  { to: "/health",    label: "Health" },
];

export function Sidebar() {
  return (
    <aside className="w-60 bg-brand-navy text-white p-5 flex flex-col">
      <div className="flex items-center gap-2 pb-6 border-b border-white/10">
        <img src="/teradata-logo.png" alt="Teradata" className="h-7 brightness-0 invert" />
      </div>
      <nav className="mt-5 space-y-1">
        {links.map((l) => (
          <NavLink
            key={l.to}
            to={l.to}
            end={l.to === "/"}
            className={({ isActive }) =>
              `block rounded px-3 py-2 text-sm transition ${
                isActive ? "bg-brand-orange text-white" : "hover:bg-white/10"
              }`
            }
          >
            {l.label}
          </NavLink>
        ))}
      </nav>
      <div className="mt-auto pt-6 text-xs text-white/60">
        Demo · React + FastAPI on Teradata Vantage
      </div>
    </aside>
  );
}
