import { createFileRoute, Link } from "@tanstack/react-router";
import { useAuth } from "../context/AuthContext";
import { bookings, grounds } from "../data/mockData";
import StatsCard from "../components/StatsCard";

export const Route = createFileRoute("/dashboard/")({ component: Dashboard });

function Dashboard() {
  const { user } = useAuth();
  if (!user) return null;
  const upcoming = bookings.filter(b => b.status === "CONFIRMED");
  const lastGrounds = grounds.slice(0, 3);

  return (
    <div>
      <h1 style={{ fontSize: 36, fontWeight: 800, textTransform: "uppercase" }}>Good Morning, {user.name.split(" ")[0]}! 👋</h1>
      <div className="dash-stats mt-6">
        <StatsCard value={user.bookings || 12} label="Total Bookings" bg="var(--yellow)" icon="📅" />
        <StatsCard value={upcoming.length} label="Upcoming" bg="var(--coral)" icon="⏰" />
        <StatsCard value={`₹${user.totalSpent || 8400}`} label="Total Spent" bg="var(--teal)" icon="💸" />
        <StatsCard value={`₹${user.wallet || 0}`} label="Wallet" bg="var(--purple)" icon="👛" />
      </div>

      <h2 className="section-title">Upcoming Bookings</h2>
      <table className="neo-table mb-4">
        <thead><tr><th>Ground</th><th>Date</th><th>Slots</th><th>Amount</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>
          {upcoming.map(b => (
            <tr key={b.id}>
              <td><b>{b.groundName}</b></td>
              <td className="mono">{b.date}</td>
              <td>{b.slots.length}</td>
              <td className="mono">₹{b.finalAmount}</td>
              <td><span className="neo-badge green">{b.status}</span></td>
              <td>
                <Link to="/dashboard/bookings" className="neo-btn sm outline">View</Link>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <h2 className="section-title mt-8">Quick Book Again</h2>
      <div className="ground-grid">
        {lastGrounds.map(g => (
          <Link key={g.id} to="/grounds/$id" params={{ id: g.id }} className="neo-card hoverable">
            <b style={{ textTransform: "uppercase" }}>{g.name}</b>
            <div style={{ fontSize: 13, color: "#666" }}>📍 {g.location}</div>
            <div className="mt-4"><span className="mono">₹{g.price}/hr</span></div>
            <button className="neo-btn block mt-4">Book Again →</button>
          </Link>
        ))}
      </div>

      <h2 className="section-title mt-8">Wallet</h2>
      <div className="neo-card" style={{ maxWidth: 480 }}>
        <div className="mono" style={{ fontSize: 36 }}>₹{user.wallet || 1250}</div>
        <div style={{ fontSize: 13, marginBottom: 12 }}>Available balance</div>
        <button className="neo-btn">+ Add Money</button>
        <div className="mt-4">
          <h4 style={{ textTransform: "uppercase", fontWeight: 800, fontSize: 13, marginBottom: 8 }}>Recent transactions</h4>
          <div className="cart-item"><span>Booking refund — Stumps & Wickets</span><span className="mono" style={{ color: "var(--green)" }}>+₹500</span></div>
          <div className="cart-item"><span>Wallet top-up</span><span className="mono" style={{ color: "var(--green)" }}>+₹1000</span></div>
          <div className="cart-item"><span>Booking — Sixer Arena</span><span className="mono" style={{ color: "var(--coral)" }}>−₹250</span></div>
        </div>
      </div>
    </div>
  );
}
