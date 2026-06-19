import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { bookings as allBookings } from "../data/mockData";

export const Route = createFileRoute("/dashboard/bookings")({ component: MyBookings });

function MyBookings() {
  const [tab, setTab] = useState<"UPCOMING"|"PAST"|"CANCELLED">("UPCOMING");
  const list = allBookings.filter(b =>
    tab === "UPCOMING" ? b.status === "CONFIRMED" :
    tab === "PAST" ? b.status === "COMPLETED" :
    b.status === "CANCELLED"
  );

  return (
    <div>
      <h1 style={{ fontSize: 32, fontWeight: 800, textTransform: "uppercase" }}>My Bookings</h1>
      <div className="flex gap-2 mt-4 mb-4">
        {(["UPCOMING","PAST","CANCELLED"] as const).map(t => (
          <button key={t} className={`neo-btn sm ${tab === t ? "" : "outline"}`} onClick={() => setTab(t)}>{t}</button>
        ))}
      </div>
      <div style={{ display: "grid", gap: 16 }}>
        {list.map(b => (
          <div key={b.id} className="neo-card hoverable">
            <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr", gap: 16, alignItems: "center" }}>
              <div>
                <h3 style={{ textTransform: "uppercase", fontWeight: 800 }}>{b.groundName}</h3>
                <div style={{ fontSize: 13, color: "#666" }}>📅 {b.date}</div>
                <div className="flex gap-2 mt-2" style={{ flexWrap: "wrap" }}>
                  {b.slots.map((s, i) => (
                    <span key={i} className="neo-badge white mono">{s.startTime}-{s.endTime}</span>
                  ))}
                </div>
              </div>
              <div>
                <span className={`neo-badge ${b.status === "CONFIRMED" ? "green" : b.status === "CANCELLED" ? "coral" : "teal"}`}>{b.status}</span>
                <div className="mono mt-2" style={{ fontSize: 12 }}>{b.ref}</div>
              </div>
              <div className="text-center">
                <div className="mono" style={{ fontSize: 22, fontWeight: 700 }}>₹{b.finalAmount}</div>
                <div className="flex gap-2 mt-2" style={{ justifyContent: "flex-end", flexWrap: "wrap" }}>
                  {tab === "UPCOMING" && <><button className="neo-btn sm">View Ticket</button><button className="neo-btn sm danger">Cancel</button></>}
                  {tab === "PAST" && <><button className="neo-btn sm">Book Again</button><button className="neo-btn sm outline">Review</button></>}
                  {tab === "CANCELLED" && <span style={{ fontSize: 12, fontWeight: 700, color: "var(--green)" }}>Refunded ₹{b.finalAmount}</span>}
                </div>
              </div>
            </div>
          </div>
        ))}
        {list.length === 0 && <div className="neo-card text-center">No {tab.toLowerCase()} bookings.</div>}
      </div>
    </div>
  );
}
