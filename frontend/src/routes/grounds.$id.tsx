import { useMemo, useState } from "react";
import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { getGround, generateSlots, reviews } from "../data/mockData";
import { useBooking } from "../context/BookingContext";
import SlotPicker from "../components/SlotPicker";
import Badge from "../components/Badge";

export const Route = createFileRoute("/grounds/$id")({
  component: GroundDetail,
  head: ({ params }) => ({ meta: [{ title: `Ground ${params.id} — BookMyBox` }] }),
});

function GroundDetail() {
  const { id } = Route.useParams();
  const ground = getGround(id);
  const today = new Date().toISOString().slice(0, 10);
  const [date, setDate] = useState(today);
  const navigate = useNavigate();
  const { selectedSlots, addSlot, removeSlot, setSelectedGround, setSelectedDate, subtotal, discount, total } = useBooking();

  const slots = useMemo(() => generateSlots(id, date), [id, date]);
  const selectedIds = selectedSlots.map(s => s.id);

  if (!ground) return <div className="container" style={{ padding: 40 }}><div className="neo-card">Ground not found.</div></div>;

  const onToggle = (slot: any) => {
    if (selectedIds.includes(slot.id)) removeSlot(slot.id);
    else addSlot(slot);
  };

  const proceed = () => {
    setSelectedGround(ground);
    setSelectedDate(date);
    navigate({ to: "/booking/$groundId", params: { groundId: ground.id } });
  };

  return (
    <div className="container" style={{ padding: "24px 24px 80px" }}>
      <div className="detail-gallery">
        <div style={{ background: ground.gradient, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 80 }}>{ground.icon}</div>
        <div style={{ background: "linear-gradient(135deg,#FFE500,#69F0AE)" }}></div>
        <div style={{ background: "linear-gradient(135deg,#B388FF,#4ECDC4)" }}></div>
      </div>

      <div className="flex between center mb-4" style={{ flexWrap: "wrap", gap: 12 }}>
        <div>
          <h1 style={{ fontSize: 40, fontWeight: 800, textTransform: "uppercase" }}>{ground.name}</h1>
          <div style={{ marginTop: 6 }}>📍 {ground.location}, {ground.city} • ★ {ground.rating} ({ground.reviewCount} reviews)</div>
        </div>
        <div className="flex gap-2">
          {ground.amenities.map(a => <Badge key={a}>{a}</Badge>)}
        </div>
      </div>

      <div className="detail-layout mt-4">
        <div>
          <div className="neo-card mb-4">
            <h3 style={{ textTransform: "uppercase", fontWeight: 800, marginBottom: 8 }}>About</h3>
            <p>{ground.description}</p>
            <h3 style={{ textTransform: "uppercase", fontWeight: 800, margin: "20px 0 8px" }}>Amenities</h3>
            <div className="amen-grid">
              {ground.amenities.map(a => <div key={a} className="item">✓ {a}</div>)}
            </div>
          </div>

          <div className="neo-card mb-4" style={{ height: 200, background: "linear-gradient(135deg,#4ECDC4,#FFE500)", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <div style={{ background: "var(--white)", padding: "12px 18px", border: "var(--border)", fontWeight: 800 }}>🗺 MAP — {ground.location}</div>
          </div>

          <h3 className="section-title" style={{ fontSize: 24 }}>Reviews</h3>
          <div style={{ display: "grid", gap: 12 }}>
            {reviews.slice(0, 3).map(r => (
              <div key={r.id} className="neo-card">
                <div style={{ color: "var(--coral)" }}>{"★".repeat(r.rating)}</div>
                <p style={{ margin: "6px 0", fontWeight: 700 }}>"{r.text}"</p>
                <div className="mono" style={{ fontSize: 13 }}>— {r.user}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="booking-widget">
          <div className="neo-card">
            <h3 style={{ textTransform: "uppercase", fontWeight: 800, marginBottom: 12 }}>Book This Ground</h3>
            <label className="neo-label">Date</label>
            <input className="neo-input mb-4" type="date" value={date} onChange={e => setDate(e.target.value)} />
            <SlotPicker slots={slots} selectedIds={selectedIds} onToggle={onToggle} />
            {selectedSlots.length > 0 && (
              <>
                <div className="mt-4" style={{ fontSize: 13, fontWeight: 700, padding: 10, background: "var(--yellow)", border: "2px solid var(--ink)" }}>
                  {selectedSlots.length >= 3 ? "✓ 10% BULK DISCOUNT APPLIED" : `ADD ${3 - selectedSlots.length} MORE FOR 10% OFF`}
                </div>
                <div className="cart-total"><span>Total</span><span>₹{total}</span></div>
              </>
            )}
            <button className="neo-btn block mt-4" disabled={selectedSlots.length === 0} onClick={proceed}>Proceed to Checkout →</button>
            <Link to="/grounds" style={{ display: "block", marginTop: 10, textAlign: "center", fontWeight: 700, textTransform: "uppercase", fontSize: 12 }}>← Back to grounds</Link>
          </div>
        </div>
      </div>
    </div>
  );
}
