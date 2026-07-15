import { NavLink } from "react-router-dom";

const links = [
  { to: "/",       label: "Overview" },
  { to: "/health", label: "Health" },
  // Add more navigation entries here.
];

export function Sidebar() {
  return (
    <aside className="w-56 bg-brand-navy text-white p-4 space-y-1 flex flex-col">
      <div className="px-2 pb-4 text-lg font-semibold">My App</div>
      {links.map((l) => (
        <NavLink
          key={l.to}
          to={l.to}
          end={l.to === "/"}
          className={({ isActive }) =>
            `block rounded px-3 py-2 text-sm ${
              isActive ? "bg-brand-orange text-white" : "hover:bg-white/10"
            }`
          }
        >
          {l.label}
        </NavLink>
      ))}
    </aside>
  );
}
