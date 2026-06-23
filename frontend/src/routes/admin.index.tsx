import { useState, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { apiAdminGetStats, apiAdminGetBookings } from "../lib/api";
import StatsCard from "../components/StatsCard";

export const Route = createFileRoute("/admin/")({ component: AdminDashboard });

function AdminDashboard() {
  const [stats, setStats] = useState<any>(null);
  const [recentBookings, setRecentBookings] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function loadStats() {
      try {
        const [statsData, bookingsData] = await Promise.all([
          apiAdminGetStats(),
          apiAdminGetBookings(undefined, undefined, 1, 5)
        ]);
        setStats(statsData);
        setRecentBookings(bookingsData.data || []);
      } catch (err) {
        console.error("Error loading admin stats:", err);
      } finally {
        setLoading(false);
      }
    }
    loadStats();
  }, []);

  if (loading) return <div className="container" style={{ padding: 40 }}><div className="neo-card">Loading admin stats...</div></div>;

  return (
    <div>
      <h1 style={{ fontSize: 32, fontWeight: 800, textTransform: "uppercase" }}>Admin Dashboard</h1>
      <div className="dash-stats mt-6" style={{ gridTemplateColumns: "repeat(3,1fr)" }}>
        <StatsCard value={`₹${stats?.revenue?.toLocaleString() || 0}`} label="Total Revenue" bg="var(--yellow)" />
        <StatsCard value={stats?.bookings_count || 0} label="Total Bookings" bg="var(--coral)" />
        <StatsCard value={stats?.grounds_count || 0} label="Total Grounds" bg="var(--teal)" />
        <StatsCard value={stats?.users_count || 0} label="Registered Users" bg="var(--purple)" />
      </div>
      
      <div className="neo-card mt-8" style={{ height: 200, background: "linear-gradient(135deg,#FFE500,#FF6B6B)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ background: "var(--white)", padding: "12px 20px", border: "var(--border)", fontWeight: 800 }}>📈 REVENUE CHART — ACTIVE</div>
      </div>

      <h2 className="section-title mt-8">Recent Bookings</h2>
      <table className="neo-table">
        <thead><tr><th>Ref</th><th>Ground</th><th>Date</th><th>Slots</th><th>Amount</th><th>Status</th></tr></thead>
        <tbody>
          {recentBookings.map(b => (
            <tr key={b.id}>
              <td className="mono">{b.ref}</td>
              <td>{b.ground?.name || "Ground"}</td>
              <td className="mono">{b.booking_date}</td>
              <td>{b.booking_slots?.length || 0}</td>
              <td className="mono">₹{b.final_amount}</td>
              <td><span className={`neo-badge ${b.status === "CONFIRMED" || b.status === "COMPLETED" ? "green" : "coral"}`}>{b.status}</span></td>
            </tr>
          ))}
          {recentBookings.length === 0 && (
            <tr>
              <td colSpan={6} className="text-center" style={{ padding: 20 }}>No bookings recorded yet.</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
}
