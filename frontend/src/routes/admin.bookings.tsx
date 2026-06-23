import { useState, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { apiAdminGetBookings, apiAdminCancelBooking } from "../lib/api";
import Modal from "../components/Modal";
import { useAuth } from "../context/AuthContext";

export const Route = createFileRoute("/admin/bookings")({ component: AdminBookings });

function AdminBookings() {
  const { pushToast } = useAuth();
  const [status, setStatus] = useState("ALL");
  const [search, setSearch] = useState("");
  const [list, setList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [detail, setDetail] = useState<any>(null);

  const fetchBookings = async () => {
    setLoading(true);
    try {
      const statusFilter = status === "ALL" ? undefined : status;
      const searchVal = search || undefined;
      const res = await apiAdminGetBookings(searchVal, statusFilter, 1, 100);
      setList(res.data || []);
    } catch (err: any) {
      pushToast(err.message || "Failed to load bookings", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookings();
  }, [status, search]);

  const cancel = async (id: string) => {
    if (!confirm("Are you sure you want to cancel this booking as Admin? An immediate full refund will be credited to the user's wallet.")) return;
    try {
      await apiAdminCancelBooking(id);
      pushToast("Booking cancelled and refunded successfully", "success");
      setDetail(null);
      fetchBookings();
    } catch (err: any) {
      pushToast(err.message || "Cancellation failed", "error");
    }
  };

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
      
      {loading ? (
        <div className="neo-card text-center" style={{ padding: 40 }}>Loading bookings...</div>
      ) : (
        <table className="neo-table">
          <thead><tr><th>Ref</th><th>Ground</th><th>Date</th><th>Slots</th><th>Amount</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            {list.map(b => (
              <tr key={b.id}>
                <td className="mono">{b.ref}</td>
                <td>{b.ground?.name || "Ground"}</td>
                <td className="mono">{b.booking_date}</td>
                <td>{b.booking_slots?.length || 0}</td>
                <td className="mono">₹{b.final_amount}</td>
                <td>
                  <span className={`neo-badge ${b.status === "CONFIRMED" || b.status === "COMPLETED" ? "green" : "coral"}`}>
                    {b.status}
                  </span>
                </td>
                <td>
                  <div className="flex gap-2">
                    <button className="neo-btn sm outline" onClick={() => setDetail(b)}>View</button>
                    {b.status === "CONFIRMED" && (
                      <button className="neo-btn sm danger" onClick={() => cancel(b.id)}>Cancel</button>
                    )}
                  </div>
                </td>
              </tr>
            ))}
            {list.length === 0 && (
              <tr>
                <td colSpan={7} className="text-center" style={{ padding: 20 }}>No bookings found.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}

      <Modal open={!!detail} onClose={() => setDetail(null)} title={`Booking ${detail?.ref || ""}`}>
        {detail && (
          <div>
            <p><b>Ground:</b> {detail.ground?.name}</p>
            <p><b>Date:</b> {detail.booking_date}</p>
            <p><b>Status:</b> {detail.status}</p>
            <div className="mt-4">
              <b>Slots:</b>
              <ul style={{ marginTop: 8 }}>
                {detail.booking_slots?.map((bs: any, i: number) => (
                  <li key={i} className="mono">
                    • {bs.slot?.start_time || ""}–{bs.slot?.end_time || ""} — ₹{bs.price}
                  </li>
                ))}
              </ul>
            </div>
            <div className="cart-total"><span>Final</span><span>₹{detail.final_amount}</span></div>
            {detail.status === "CONFIRMED" && (
              <button className="neo-btn danger mt-4" onClick={() => cancel(detail.id)}>Refund & Cancel</button>
            )}
          </div>
        )}
      </Modal>
    </div>
  );
}
