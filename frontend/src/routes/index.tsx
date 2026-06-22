import { createFileRoute, Link } from "@tanstack/react-router";
import { grounds, reviews } from "../data/mockData";
import GroundCard from "../components/GroundCard";
import StatsCard from "../components/StatsCard";
import { useAuth } from "../context/AuthContext";

export const Route = createFileRoute("/")({ component: Landing });

function Landing() {
  const { user } = useAuth();
  return (
    <>
      <section className="hero">
        <div className="container">
          <div className="hero-grid">
            <div style={{ position: "relative" }}>
              <span className="hero-deco square" style={{ position: "relative", display: "inline-block", marginBottom: 16, transform: "none" }}></span>
              <h1>
                Book Your Box
                <span className="stroke">Cricket Ground</span>
              </h1>
              <p className="lede">Reserve slots instantly. Pay online. Play now. The fastest way to book box cricket in your city.</p>
              <div className="hero-ctas">
                {user ? (
                  <Link to="/grounds" className="neo-btn lg">Find a Ground →</Link>
                ) : (
                  <Link to="/login" search={{ role: "user" }} className="neo-btn lg">Find a Ground →</Link>
                )}
                {user && user.role === "admin" ? (
                  <Link to="/add-ground" className="neo-btn lg outline">Add Your Ground →</Link>
                ) : (
                  <Link to="/login" search={{ role: "admin" }} className="neo-btn lg outline">Add Your Ground →</Link>
                )}
              </div>
            </div>
            <div style={{ position: "relative" }}>
              <div className="hero-deco circle" style={{ position: "absolute", top: -20, right: -20 }}></div>
              <div className="preview-card">
                <div className="img">🏏</div>
                <div className="body">
                  <div className="row"><b>Sixer Arena</b><span className="neo-badge coral">POPULAR</span></div>
                  <div className="row"><span>📍 Hitech City</span><span>★ 4.7</span></div>
                  <div className="row"><span>Tonight 7PM</span><span className="mono">3 slots</span></div>
                  <div className="row"><span className="mono" style={{ fontSize: 22 }}>₹800/hr</span><button className="neo-btn sm">Book</button></div>
                </div>
              </div>
            </div>
          </div>

          <div className="stats-row">
            <StatsCard value="50+" label="Grounds" bg="var(--yellow)" />
            <StatsCard value="10K+" label="Players" bg="var(--coral)" />
            <StatsCard value="60s" label="To Book" bg="var(--teal)" />
            <StatsCard value="₹500+" label="Onwards" bg="var(--purple)" />
          </div>
        </div>
      </section>

      <section className="container" id="how" style={{ padding: "60px 24px" }}>
        <h2 className="section-title">How it Works</h2>
        <div className="how-grid">
          {[
            { n: "01", t: "Search Ground", d: "Filter by location, price, and amenities.", i: "🔍" },
            { n: "02", t: "Pick Slots", d: "Select one or more time slots in one go.", i: "🕒" },
            { n: "03", t: "Pay Online", d: "UPI, cards, or net banking — your choice.", i: "💳" },
            { n: "04", t: "Play!", d: "Show your ticket and hit the turf.", i: "🏏" },
          ].map(s => (
            <div key={s.n} className="how-step">
              <div className="step-num">{s.n}</div>
              <div style={{ fontSize: 28 }}>{s.i}</div>
              <h3>{s.t}</h3>
              <p style={{ fontSize: 14 }}>{s.d}</p>
            </div>
          ))}
        </div>
      </section>

      <section className="container" style={{ padding: "20px 24px 60px" }}>
        <div className="flex between center mb-4" style={{ flexWrap: "wrap", gap: 12 }}>
          <h2 className="section-title" style={{ marginBottom: 0 }}>Top Grounds This Week</h2>
          <Link to="/grounds" className="neo-btn outline">View all →</Link>
        </div>
        <div className="ground-grid">
          {grounds.slice(0, 3).map(g => <GroundCard key={g.id} g={g} />)}
        </div>
      </section>

      <section className="dark-section">
        <div className="container">
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 48, alignItems: "center" }}>
            <div>
              <h2 className="section-title" style={{ color: "var(--yellow)", borderColor: "var(--coral)" }}>Book Multiple Slots — One Checkout</h2>
              <ul style={{ display: "grid", gap: 12, fontSize: 16 }}>
                <li>✓ Add 1, 2, or 6 slots to a single cart</li>
                <li>✓ Auto-applied 10% off on 3+ slot bookings</li>
                <li>✓ Partial cancellation: refund any slot anytime</li>
                <li>✓ Pay once, play all day</li>
              </ul>
            </div>
            <div style={{ display: "grid", gap: 10 }}>
              {["18:00 – 19:00", "19:00 – 20:00", "20:00 – 21:00"].map(t => (
                <div key={t} className="slot selected" style={{ background: "var(--yellow)" }}>
                  <span className="t">{t} ✓</span>
                  <span className="p">₹800</span>
                </div>
              ))}
              <div className="cart-total" style={{ background: "var(--white)", padding: 12, color: "var(--ink)", border: "var(--border)" }}>
                <span>Total</span><span>₹2160 <small style={{ color: "var(--coral)" }}>−10%</small></span>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="container" style={{ padding: "60px 24px" }}>
        <h2 className="section-title">What Players Say</h2>
        <div className="ground-grid">
          {reviews.slice(0, 3).map(r => (
            <div key={r.id} className="neo-card hoverable">
              <div style={{ color: "var(--coral)", fontSize: 20 }}>{"★".repeat(r.rating)}</div>
              <p style={{ fontWeight: 700, margin: "12px 0", fontSize: 18 }}>"{r.text}"</p>
              <div className="mono">— {r.user}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="container text-center" style={{ padding: "60px 24px" }}>
        <div style={{ fontSize: 64, fontWeight: 800, textTransform: "uppercase", letterSpacing: "-0.03em" }} className="mono">Starts at ₹500/hr</div>
        <p style={{ fontSize: 18, margin: "12px 0 24px" }}>No hidden fees. No subscriptions.</p>
        <Link to="/grounds" className="neo-btn lg">Book Now →</Link>
      </section>
    </>
  );
}
