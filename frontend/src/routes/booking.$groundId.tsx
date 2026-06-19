import { useMemo, useState } from "react";
import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { getGround, generateSlots } from "../data/mockData";
import { useBooking } from "../context/BookingContext";
import { useAuth } from "../context/AuthContext";
import SlotPicker from "../components/SlotPicker";
import BookingCart from "../components/BookingCart";

export const Route = createFileRoute("/booking/$groundId")({ component: BookingFlow });

const STEPS = ["Select Date", "Pick Slots", "Review", "Pay", "Done"];

function BookingFlow() {
  const { groundId } = Route.useParams();
  const ground = getGround(groundId);
  const navigate = useNavigate();
  const { user, pushToast } = useAuth();
  const { selectedDate, setSelectedDate, selectedSlots, addSlot, removeSlot, clearSlots, subtotal, discount, total, setSelectedGround } = useBooking();
  const [step, setStep] = useState(selectedDate ? 1 : 0);
  const [payMethod, setPayMethod] = useState("upi");
  const [ref, setRef] = useState("");

  const slots = useMemo(() => selectedDate ? generateSlots(groundId, selectedDate) : [], [groundId, selectedDate]);
  const selectedIds = selectedSlots.map(s => s.id);

  if (!ground) return <div className="container" style={{ padding: 40 }}><div className="neo-card">Ground not found.</div></div>;

  // generate calendar grid for current month
  const monthDays = useMemo(() => {
    const now = new Date();
    const year = now.getFullYear(); const month = now.getMonth();
    const first = new Date(year, month, 1);
    const days: ({ d: string; past: boolean } | null)[] = [];
    for (let i = 0; i < first.getDay(); i++) days.push(null);
    const last = new Date(year, month + 1, 0).getDate();
    for (let i = 1; i <= last; i++) {
      const dateStr = new Date(year, month, i).toISOString().slice(0,10);
      const past = new Date(year, month, i) < new Date(now.getFullYear(), now.getMonth(), now.getDate());
      days.push({ d: dateStr, past });
    }
    return days;
  }, []);

  const monthName = new Date().toLocaleDateString("en-US", { month: "long", year: "numeric" });

  const onPay = () => {
    if (!user) { pushToast("Please log in to complete payment", "error"); navigate({ to: "/login" }); return; }
    const newRef = `BMB-2026-${Math.floor(10000 + Math.random() * 89999)}`;
    setRef(newRef);
    setStep(4);
    pushToast("Payment successful!", "success");
  };

  return (
    <div className="container" style={{ padding: "32px 24px 80px" }}>
      <Link to="/grounds/$id" params={{ id: ground.id }} style={{ fontWeight: 700, textTransform: "uppercase", fontSize: 12 }}>← Back to ground</Link>
      <h1 style={{ fontSize: 36, fontWeight: 800, textTransform: "uppercase", margin: "8px 0" }}>{ground.name}</h1>

      <div className="steps">
        {STEPS.map((s, i) => (
          <div key={s} className={`step ${i === step ? "current" : i < step ? "done" : ""}`}>{i+1}. {s}</div>
        ))}
      </div>

      {step === 0 && (
        <div className="neo-card" style={{ maxWidth: 560 }}>
          <h2 style={{ textTransform: "uppercase", fontWeight: 800, marginBottom: 12 }}>{monthName}</h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(7,1fr)", gap: 6 }}>
            {["S","M","T","W","T","F","S"].map(d => <div key={d} style={{ textAlign: "center", fontWeight: 800, padding: 6 }}>{d}</div>)}
            {monthDays.map((day, i) => day ? (
              <button key={i}
                disabled={day.past}
                onClick={() => { setSelectedDate(day.d); setSelectedGround(ground); clearSlots(); setStep(1); }}
                style={{
                  padding: 10, border: "2px solid var(--ink)",
                  background: selectedDate === day.d ? "var(--yellow)" : day.past ? "#eee" : "var(--white)",
                  textDecoration: day.past ? "line-through" : "none",
                  cursor: day.past ? "not-allowed" : "pointer",
                  fontWeight: 700,
                }}>
                {day.d.slice(-2)}
              </button>
            ) : <div key={i}></div>)}
          </div>
        </div>
      )}

      {step === 1 && (
        <div className="detail-layout">
          <div>
            <div className="neo-card mb-4">
              <div className="flex between center mb-4">
                <div><b>Date:</b> {selectedDate}</div>
                <button className="neo-btn sm outline" onClick={() => setStep(0)}>Change date</button>
              </div>
              <SlotPicker slots={slots} selectedIds={selectedIds} onToggle={(s: any) => selectedIds.includes(s.id) ? removeSlot(s.id) : addSlot(s)} />
            </div>
          </div>
          <BookingCart onContinue={() => selectedSlots.length && setStep(2)} />
        </div>
      )}

      {step === 2 && (
        <div className="neo-card" style={{ maxWidth: 680 }}>
          <h2 style={{ textTransform: "uppercase", fontWeight: 800 }}>Review Your Booking</h2>
          <div className="mt-4"><b>Ground:</b> {ground.name} — {ground.location}</div>
          <div><b>Date:</b> {selectedDate}</div>
          <div className="mt-4" style={{ display: "grid", gap: 8 }}>
            {selectedSlots.map(s => (
              <div key={s.id} className="cart-item">
                <span className="mono">{s.startTime}–{s.endTime}</span>
                <span>₹{s.price} <button onClick={() => removeSlot(s.id)} style={{ color: "var(--coral)", fontWeight: 800, marginLeft: 8 }}>✕</button></span>
              </div>
            ))}
          </div>
          <div className="cart-item"><span>Subtotal</span><span className="mono">₹{subtotal}</span></div>
          {discount > 0 && <div className="cart-item" style={{ color: "var(--coral)" }}><span>Discount</span><span className="mono">−₹{discount}</span></div>}
          <div className="cart-total"><span>Total</span><span>₹{total}</span></div>
          <p style={{ marginTop: 16, padding: 12, background: "var(--light)", border: "2px solid var(--ink)", fontSize: 13 }}>
            <b>CANCELLATION POLICY:</b> Free cancellation up to 6 hours before slot start. Partial slot cancellation supported.
          </p>
          <div className="flex gap-3 mt-4">
            <button className="neo-btn outline" onClick={() => setStep(1)}>← Back</button>
            <button className="neo-btn" onClick={() => setStep(3)}>Proceed to Payment →</button>
          </div>
        </div>
      )}

      {step === 3 && (
        <div className="detail-layout">
          <div className="neo-card">
            <h2 style={{ textTransform: "uppercase", fontWeight: 800, marginBottom: 16 }}>Payment</h2>
            <div className="flex gap-2 mb-4" style={{ flexWrap: "wrap" }}>
              {[["upi","UPI"],["card","Card"],["nb","Net Banking"],["wallet","Wallet"]].map(([v,l]) => (
                <button key={v} className={`neo-btn sm ${payMethod === v ? "" : "outline"}`} onClick={() => setPayMethod(v)}>{l}</button>
              ))}
            </div>
            {payMethod === "upi" && (
              <>
                <input className="neo-input mb-4" placeholder="yourname@upi" />
                <div className="neo-card text-center" style={{ background: "var(--light)" }}>
                  <div style={{ fontSize: 60 }}>▦</div>
                  <div className="mono">SCAN TO PAY</div>
                </div>
              </>
            )}
            {payMethod === "card" && (
              <>
                <input className="neo-input mb-4" placeholder="Card number" />
                <div className="form-row">
                  <input className="neo-input" placeholder="MM/YY" />
                  <input className="neo-input" placeholder="CVV" />
                </div>
                <input className="neo-input mt-4" placeholder="Cardholder name" />
              </>
            )}
            {payMethod === "nb" && <select className="neo-input"><option>Select Bank</option><option>HDFC</option><option>SBI</option><option>ICICI</option></select>}
            {payMethod === "wallet" && <div className="neo-card">Wallet balance: <span className="mono">₹1250</span></div>}
          </div>
          <div className="cart">
            <h3 style={{ textTransform: "uppercase", fontWeight: 800, marginBottom: 12 }}>Order Summary</h3>
            {selectedSlots.map(s => <div key={s.id} className="cart-item"><span className="mono">{s.startTime}</span><span>₹{s.price}</span></div>)}
            <div className="cart-item"><span>Subtotal</span><span className="mono">₹{subtotal}</span></div>
            {discount > 0 && <div className="cart-item" style={{ color: "var(--coral)" }}><span>Discount</span><span className="mono">−₹{discount}</span></div>}
            <div className="flex gap-2 mt-4">
              <input className="neo-input" placeholder="Promo code" />
              <button className="neo-btn sm outline">Apply</button>
            </div>
            <div className="cart-total"><span>Total</span><span>₹{total}</span></div>
            <button className="neo-btn block lg mt-4" onClick={onPay}>Pay ₹{total} →</button>
          </div>
        </div>
      )}

      {step === 4 && (
        <div className="neo-card text-center" style={{ maxWidth: 560, margin: "0 auto" }}>
          <div style={{ width: 80, height: 80, borderRadius: "50%", background: "var(--yellow)", border: "var(--border)", margin: "0 auto", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 40, fontWeight: 800 }}>✓</div>
          <h1 style={{ fontSize: 32, fontWeight: 800, textTransform: "uppercase", margin: "16px 0" }}>Booking Confirmed!</h1>
          <div className="mono" style={{ fontSize: 18, padding: "8px 16px", background: "var(--yellow)", border: "2px solid var(--ink)", display: "inline-block" }}>{ref}</div>
          <div className="mt-4" style={{ textAlign: "left" }}>
            <div><b>Ground:</b> {ground.name}</div>
            <div><b>Date:</b> {selectedDate}</div>
            <div><b>Slots:</b> {selectedSlots.map(s => `${s.startTime}-${s.endTime}`).join(", ")}</div>
            <div><b>Amount Paid:</b> ₹{total}</div>
          </div>
          <div className="flex gap-3 mt-6" style={{ justifyContent: "center", flexWrap: "wrap" }}>
            <button className="neo-btn dark">Download Ticket</button>
            <button className="neo-btn" onClick={() => { clearSlots(); navigate({ to: "/grounds" }); }}>Book Another</button>
          </div>
          <Link to="/dashboard/bookings" style={{ display: "block", marginTop: 16, fontWeight: 700, textTransform: "uppercase", fontSize: 12 }}>View in My Bookings →</Link>
        </div>
      )}
    </div>
  );
}
