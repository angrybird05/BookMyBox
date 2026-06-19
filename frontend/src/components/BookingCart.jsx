import { useBooking } from "../context/BookingContext";

export default function BookingCart({ onContinue, continueLabel = "Continue to Review →" }) {
  const { selectedSlots, removeSlot, clearSlots, subtotal, discount, total } = useBooking();
  return (
    <div className="cart">
      <h3 style={{ textTransform: "uppercase", fontWeight: 800, marginBottom: 12 }}>Your Cart</h3>
      {selectedSlots.length === 0 && <p style={{ fontSize: 14, color: "#666" }}>No slots selected yet.</p>}
      {selectedSlots.map(s => (
        <div key={s.id} className="cart-item">
          <span className="mono">{s.startTime}–{s.endTime}</span>
          <span>₹{s.price} <button onClick={() => removeSlot(s.id)} style={{ color: "var(--coral)", fontWeight: 800, marginLeft: 8 }}>✕</button></span>
        </div>
      ))}
      {selectedSlots.length > 0 && (
        <>
          <div className="cart-item"><span>Subtotal</span><span className="mono">₹{subtotal}</span></div>
          {discount > 0 && <div className="cart-item" style={{ color: "var(--coral)" }}><span>Bulk discount (10%)</span><span className="mono">−₹{discount}</span></div>}
          <div className="cart-total"><span>Total</span><span>₹{total}</span></div>
          {selectedSlots.length < 3 && (
            <div style={{ marginTop: 12, padding: 10, background: "var(--yellow)", border: "2px solid var(--ink)", fontSize: 12, fontWeight: 700 }}>
              ADD {3 - selectedSlots.length} MORE SLOT(S) FOR 10% OFF
            </div>
          )}
          <button className="neo-btn block mt-4" onClick={onContinue}>{continueLabel}</button>
          <button onClick={clearSlots} style={{ marginTop: 10, fontSize: 12, fontWeight: 700, textTransform: "uppercase", color: "var(--coral)" }}>Clear all</button>
        </>
      )}
    </div>
  );
}
