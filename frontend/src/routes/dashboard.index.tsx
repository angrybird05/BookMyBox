import { useState, useEffect } from "react";
import { createFileRoute, Link } from "@tanstack/react-router";
import { useAuth } from "../context/AuthContext";
import { apiGetMeStats, apiGetMyBookings, apiGetWalletTransactions, apiGetTopGrounds } from "../lib/api";
import StatsCard from "../components/StatsCard";

export const Route = createFileRoute("/dashboard/")({ component: Dashboard });

function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState<any>(null);
  const [upcoming, setUpcoming] = useState<any[]>([]);
  const [transactions, setTransactions] = useState<any[]>([]);
  const [lastGrounds, setLastGrounds] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (!user) return;
    async function loadDashData() {
      try {
        const [statsData, bookingsData, txData, groundsData] = await Promise.all([
          apiGetMeStats(),
          apiGetMyBookings("UPCOMING", 1, 5),
          apiGetWalletTransactions(1, 3),
          apiGetTopGrounds(3)
        ]);
        setStats(statsData);
        setUpcoming(bookingsData.data || []);
        setTransactions(txData.data || []);
        setLastGrounds(groundsData);
      } catch (err) {
        console.error("Error loading dashboard data:", err);
      } finally {
        setLoading(false);
      }
    }
    loadDashData();
  }, [user]);

  if (!user) return null;
  if (loading) return <div className="container" style={{ padding: 40 }}><div className="neo-card">Loading dashboard...</div></div>;

  return (
    <div>
      <h1 style={{ fontSize: 36, fontWeight: 800, textTransform: "uppercase" }}>Good Morning, {user.name.split(" ")[0]}! 👋</h1>
      <div className="dash-stats mt-6">
        <StatsCard value={stats?.bookings_count || 0} label="Total Bookings" bg="var(--yellow)" icon="📅" />
        <StatsCard value={upcoming.length} label="Upcoming" bg="var(--coral)" icon="⏰" />
        <StatsCard value={`₹${stats?.total_spent || 0}`} label="Total Spent" bg="var(--teal)" icon="💸" />
        <StatsCard value={`₹${stats?.wallet_balance || 0}`} label="Wallet" bg="var(--purple)" icon="👛" />
      </div>

      <h2 className="section-title">Upcoming Bookings</h2>
      <table className="neo-table mb-4">
        <thead><tr><th>Ground</th><th>Date</th><th>Slots</th><th>Amount</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>
          {upcoming.map(b => (
            <tr key={b.id}>
              <td><b>{b.ground?.name || "Box Ground"}</b></td>
              <td className="mono">{b.booking_date}</td>
              <td>{b.booking_slots?.length || 0}</td>
              <td className="mono">₹{b.final_amount}</td>
              <td><span className="neo-badge green">{b.status}</span></td>
              <td>
                <Link to="/dashboard/bookings" className="neo-btn sm outline">View</Link>
              </td>
            </tr>
          ))}
          {upcoming.length === 0 && (
            <tr>
              <td colSpan={6} className="text-center" style={{ padding: 20 }}>No upcoming bookings.</td>
            </tr>
          )}
        </tbody>
      </table>

      <h2 className="section-title mt-8">Quick Book Again</h2>
      <div className="ground-grid">
        {lastGrounds.map(g => (
          <Link key={g.id} to="/grounds/$id" params={{ id: g.id }} className="neo-card hoverable">
            <b style={{ textTransform: "uppercase" }}>{g.name}</b>
            <div style={{ fontSize: 13, color: "#666" }}>📍 {g.location}</div>
            <div className="mt-4"><span className="mono">₹{g.price_per_hour}/hr</span></div>
            <button className="neo-btn block mt-4">Book Again →</button>
          </Link>
        ))}
      </div>

      <h2 className="section-title mt-8">Wallet</h2>
      <div className="neo-card" style={{ maxWidth: 480 }}>
        <div className="mono" style={{ fontSize: 36 }}>₹{stats?.wallet_balance || 0}</div>
        <div style={{ fontSize: 13, marginBottom: 12 }}>Available balance</div>
        <Link to="/dashboard/profile" className="neo-btn" style={{ display: "inline-block", textAlign: "center" }}>+ Add Money / Manage Wallet</Link>
        <div className="mt-4">
          <h4 style={{ textTransform: "uppercase", fontWeight: 800, fontSize: 13, marginBottom: 8 }}>Recent transactions</h4>
          {transactions.map(t => (
            <div key={t.id} className="cart-item">
              <span>{t.description || "Wallet Transaction"}</span>
              <span className="mono" style={{ color: t.type === "CREDIT" ? "var(--green)" : "var(--coral)" }}>
                {t.type === "CREDIT" ? "+" : "−"}₹{t.amount}
              </span>
            </div>
          ))}
          {transactions.length === 0 && <div style={{ fontSize: 13, color: "#666" }}>No wallet transactions yet.</div>}
        </div>
      </div>
    </div>
  );
}
