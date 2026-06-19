import { Link, Outlet, createFileRoute, useLocation, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { useAuth } from "../context/AuthContext";

export const Route = createFileRoute("/dashboard")({ component: DashLayout });

function DashLayout() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const { pathname } = useLocation();

  useEffect(() => { if (!user) navigate({ to: "/login" }); }, [user, navigate]);
  if (!user) return null;

  const initials = user.name.split(" ").map(p => p[0]).slice(0, 2).join("").toUpperCase();
  const nav = [
    { to: "/dashboard", label: "🏠 Dashboard", exact: true },
    { to: "/dashboard/bookings", label: "📅 My Bookings" },
    { to: "/dashboard/profile", label: "👤 Profile" },
  ];

  return (
    <div className="container dash-layout">
      <aside className="dash-sidebar">
        <div className="avatar">{initials}</div>
        <div className="name">{user.name}</div>
        <div className="text-center mt-2"><span className="neo-badge purple">Premium</span></div>
        <nav className="dash-nav">
          {nav.map(n => {
            const active = n.exact ? pathname === n.to : pathname.startsWith(n.to);
            return <Link key={n.to} to={n.to} className={active ? "active" : ""}>{n.label}</Link>;
          })}
        </nav>
      </aside>
      <div><Outlet /></div>
    </div>
  );
}
