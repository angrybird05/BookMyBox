import { createFileRoute } from "@tanstack/react-router";
import { adminStats, bookings } from "../data/mockData";
import StatsCard from "../components/StatsCard";

export const Route = createFileRoute("/admin/")({ component: AdminDashboard });

function AdminDashboard() {
  return (
    <div>
      <h1 style={{ fontSize: 32, fontWeight: 800, textTransform: "uppercase" }}>Admin Dashboard</h1>
      <div className="dash-stats mt-6" style={{ gridTemplateColumns: "repeat(3,1fr)" }}>
        <StatsCard value={`₹${adminStats.totalRevenue.toLocaleString()}`} label="Total Revenue" bg="var(--yellow)" />
        <StatsCard value={adminStats.totalBookings} label="Total Bookings" bg="var(--coral)" />
        <StatsCard value={adminStats.activeGrounds} label="Active Grounds" bg="var(--teal)" />
        <StatsCard value={adminStats.activeUsers} label="Active Users" bg="var(--purple)" />
        <StatsCard value={adminStats.todayBookings} label="Today" bg="var(--green)" />
        <StatsCard value={adminStats.pendingCancellations} label="Pending Refunds" bg="var(--white)" />
      </div>
      <div className="neo-card mt-8" style={{ height: 240, background: "linear-gradient(135deg,#FFE500,#FF6B6B)", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <div style={{ background: "var(--white)", padding: "12px 20px", border: "var(--border)", fontWeight: 800 }}>📈 REVENUE CHART — LAST 30 DAYS</div>
      </div>

      <h2 className="section-title mt-8">Recent Bookings</h2>
      <table className="neo-table">
        <thead><tr><th>Ref</th><th>Ground</th><th>Date</th><th>Slots</th><th>Amount</th><th>Status</th></tr></thead>
        <tbody>
          {bookings.map(b => (
            <tr key={b.id}>
              <td className="mono">{b.ref}</td>
              <td>{b.groundName}</td>
              <td className="mono">{b.date}</td>
              <td>{b.slots.length}</td>
              <td className="mono">₹{b.finalAmount}</td>
              <td><span className={`neo-badge ${b.status === "CONFIRMED" ? "green" : b.status === "CANCELLED" ? "coral" : "teal"}`}>{b.status}</span></td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="flex gap-3 mt-6" style={{ flexWrap: "wrap" }}>
        <button className="neo-btn">+ Add Ground</button>
        <button className="neo-btn secondary">Manage Slots</button>
        <button className="neo-btn outline">View Reports</button>
      </div>
    </div>
  );
}
