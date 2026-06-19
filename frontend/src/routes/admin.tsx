import { useEffect } from "react";
import { Link, Outlet, createFileRoute, useLocation, useNavigate } from "@tanstack/react-router";
import { useAuth } from "../context/AuthContext";

export const Route = createFileRoute("/admin")({ component: AdminLayout });

function AdminLayout() {
  const { user, isAdmin } = useAuth();
  const navigate = useNavigate();
  const { pathname } = useLocation();

  useEffect(() => {
    if (!user) navigate({ to: "/login" });
    else if (!isAdmin) navigate({ to: "/dashboard" });
  }, [user, isAdmin, navigate]);

  if (!user || !isAdmin) return null;

  const nav = [
    { to: "/admin", label: "Dashboard", exact: true },
    { to: "/admin/grounds", label: "Grounds" },
    { to: "/admin/slots", label: "Slots" },
    { to: "/admin/bookings", label: "Bookings" },
    { to: "/admin/users", label: "Users" },
  ];

  return (
    <div className="container dash-layout" style={{ gridTemplateColumns: "260px 1fr" }}>
      <aside className="dash-sidebar" style={{ padding: 0 }}>
        <div style={{ background: "var(--ink)", color: "var(--yellow)", padding: 16, fontWeight: 800, textTransform: "uppercase", textAlign: "center", letterSpacing: "0.05em" }}>Admin Panel</div>
        <nav className="dash-nav" style={{ padding: 12 }}>
          {nav.map(n => {
            const active = n.exact ? pathname === n.to : pathname.startsWith(n.to);
            return (
              <Link key={n.to} to={n.to} className={active ? "active" : ""} style={active ? { borderLeft: "4px solid var(--ink)" } : undefined}>
                {n.label}
              </Link>
            );
          })}
        </nav>
      </aside>
      <div><Outlet /></div>
    </div>
  );
}
