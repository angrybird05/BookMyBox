import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { bookings } from "../data/mockData";
import Modal from "../components/Modal";

export const Route = createFileRoute("/admin/bookings")({ component: AdminBookings });

function AdminBookings() {
  const [status, setStatus] = useState("ALL");
  const [search, setSearch] = useState("");
  const [detail, setDetail] = useState<any>(null);

  const list = bookings.filter(b =>
    (status === "ALL" || b.status === status) &&
    (!search || b.ref.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <div>
      <h1 style={{ fontSize: 32, fontWeight: 800, textTransform: "uppercase" }}>Bookings</h1>
      <div className="neo-card mt-4 mb-4">
        <div className="form-row">
          <input className="neo-input" placeholder="Search by ref…" value={search} onChange={e => setSearch(e.target.value)} />
          <select className="neo-input" value={status} onChange={e => setStatus(e.target.value)}>
            <option value="ALL">All statuses</option>
            <option value="CONFIRMED">Confirmed</option>
            <option value="COMPLETED">Completed</option>
            <option value="CANCELLED">Cancelled</option>
          </select>
        </div>
      </div>
      <table className="neo-table">
        <thead><tr><th>Ref</th><th>Ground</th><th>Date</th><th>Slots</th><th>Amount</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>
          {list.map(b => (
            <tr key={b.id}>
              <td className="mono">{b.ref}</td>
              <td>{b.groundName}</td>
              <td className="mono">{b.date}</td>
              <td>{b.slots.length}</td>
              <td className="mono">₹{b.finalAmount}</td>
              <td><span className={`neo-badge ${b.status === "CONFIRMED" ? "green" : b.status === "CANCELLED" ? "coral" : "teal"}`}>{b.status}</span></td>
              <td>
                <div className="flex gap-2">
                  <button className="neo-btn sm outline" onClick={() => setDetail(b)}>View</button>
                  <button className="neo-btn sm danger">Cancel</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Modal open={!!detail} onClose={() => setDetail(null)} title={`Booking ${detail?.ref || ""}`}>
        {detail && (
          <div>
            <p><b>Ground:</b> {detail.groundName}</p>
            <p><b>Date:</b> {detail.date}</p>
            <p><b>Status:</b> {detail.status}</p>
            <div className="mt-4">
              <b>Slots:</b>
              <ul style={{ marginTop: 8 }}>
                {detail.slots.map((s: any, i: number) => <li key={i} className="mono">• {s.startTime}–{s.endTime} — ₹{s.price}</li>)}
              </ul>
            </div>
            <div className="cart-total"><span>Final</span><span>₹{detail.finalAmount}</span></div>
            <button className="neo-btn danger mt-4">Refund</button>
          </div>
        )}
      </Modal>
    </div>
  );
}
