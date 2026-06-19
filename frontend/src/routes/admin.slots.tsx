import { useMemo, useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { grounds, generateSlots } from "../data/mockData";

export const Route = createFileRoute("/admin/slots")({ component: AdminSlots });

function AdminSlots() {
  const [groundId, setGroundId] = useState(grounds[0].id);
  const [date, setDate] = useState(new Date().toISOString().slice(0,10));
  const [blocked, setBlocked] = useState<Record<string, boolean>>({});
  const slots = useMemo(() => generateSlots(groundId, date), [groundId, date]);

  const toggleBlock = (id: string) => setBlocked(b => ({ ...b, [id]: !b[id] }));

  return (
    <div>
      <h1 style={{ fontSize: 32, fontWeight: 800, textTransform: "uppercase" }}>Slot Management</h1>
      <div className="neo-card mt-4">
        <div className="form-row">
          <div className="field">
            <label className="neo-label">Ground</label>
            <select className="neo-input" value={groundId} onChange={e => setGroundId(e.target.value)}>
              {grounds.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
            </select>
          </div>
          <div className="field"><label className="neo-label">Date</label><input className="neo-input" type="date" value={date} onChange={e => setDate(e.target.value)} /></div>
        </div>
        <div className="flex gap-3 mb-4" style={{ flexWrap: "wrap" }}>
          <button className="neo-btn sm danger">Block All</button>
          <button className="neo-btn sm secondary">Unblock All</button>
          <button className="neo-btn sm">Set Price</button>
          <input className="neo-input" placeholder="Buffer (min)" style={{ width: 160 }} />
        </div>
        <div className="slot-grid">
          {slots.map(s => {
            const isBlocked = blocked[s.id];
            const cls = ["slot", s.status === "booked" ? "booked" : isBlocked ? "selected" : ""].join(" ");
            return (
              <button key={s.id} className={cls} disabled={s.status === "booked"} onClick={() => toggleBlock(s.id)} style={isBlocked ? { background: "var(--coral)", color: "var(--white)" } : undefined}>
                <span className="t">{s.startTime}–{s.endTime}</span>
                <span className="p">{s.status === "booked" ? "BOOKED" : isBlocked ? "BLOCKED" : "AVAILABLE"} • ₹{s.price}</span>
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}
