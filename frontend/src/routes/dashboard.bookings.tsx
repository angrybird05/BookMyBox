import { useState, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { apiGetMyBookings, apiCancelBooking, apiDownloadTicket } from "../lib/api";
import { useAuth } from "../context/AuthContext";

export const Route = createFileRoute("/dashboard/bookings")({ component: MyBookings });

function MyBookings() {
  const { pushToast } = useAuth();
  const [tab, setTab] = useState<"UPCOMING"|"PAST"|"CANCELLED">("UPCOMING");
  const [bookingsList, setBookingsList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchBookings = async () => {
    setLoading(true);
    try {
      // Map tab values to backend expectations: tab can be UPCOMING, PAST, CANCELLED
      const res = await apiGetMyBookings(tab);
      setBookingsList(res.data || []);
    } catch (err: any) {
      pushToast(err.message || "Failed to load bookings", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBookings();
  }, [tab]);

  const cancel = async (id: string) => {
    if (!confirm("Are you sure you want to cancel this entire booking? The amount will be refunded to your wallet.")) return;
    try {
      await apiCancelBooking(id);
      pushToast("Booking cancelled successfully and amount refunded!", "success");
      fetchBookings();
    } catch (err: any) {
      pushToast(err.message || "Cancellation failed", "error");
    }
  };

  const handleDownloadTicket = async (id: string, ref: string) => {
    try {
      const blob = await apiDownloadTicket(id);
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `BMB_Ticket_${ref}.pdf`;
      document.body.appendChild(a);
      a.click();
      a.remove();
      window.URL.revokeObjectURL(url);
      pushToast("Ticket downloaded successfully", "success");
    } catch (err: any) {
      pushToast(err.message || "Download failed", "error");
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: 32, fontWeight: 800, textTransform: "uppercase" }}>My Bookings</h1>
      <div className="flex gap-2 mt-4 mb-4">
        {(["UPCOMING","PAST","CANCELLED"] as const).map(t => (
          <button key={t} className={`neo-btn sm ${tab === t ? "" : "outline"}`} onClick={() => setTab(t)}>{t}</button>
        ))}
      </div>
      
      {loading ? (
        <div className="neo-card text-center" style={{ padding: 40 }}>Loading bookings...</div>
      ) : (
        <div style={{ display: "grid", gap: 16 }}>
          {bookingsList.map(b => (
            <div key={b.id} className="neo-card hoverable">
              <div style={{ display: "grid", gridTemplateColumns: "2fr 1fr 1fr", gap: 16, alignItems: "center" }}>
                <div>
                  <h3 style={{ textTransform: "uppercase", fontWeight: 800 }}>{b.ground?.name || "Ground"}</h3>
                  <div style={{ fontSize: 13, color: "#666" }}>📅 {b.booking_date}</div>
                  <div className="flex gap-2 mt-2" style={{ flexWrap: "wrap" }}>
                    {b.booking_slots?.map((bs: any, i: number) => (
                      <span key={i} className="neo-badge white mono">
                        {bs.slot?.start_time || bs.slot_id?.slice(0, 5)}–{bs.slot?.end_time || ""}
                      </span>
                    ))}
                  </div>
                </div>
                <div>
                  <span className={`neo-badge ${b.status === "CONFIRMED" || b.status === "COMPLETED" ? "green" : "coral"}`}>{b.status}</span>
                  <div className="mono mt-2" style={{ fontSize: 12 }}>{b.ref}</div>
                </div>
                <div className="text-center">
                  <div className="mono" style={{ fontSize: 22, fontWeight: 700 }}>₹{b.final_amount}</div>
                  <div className="flex gap-2 mt-2" style={{ justifyContent: "flex-end", flexWrap: "wrap" }}>
                    {(b.status === "CONFIRMED" || b.status === "COMPLETED") && (
                      <button className="neo-btn sm" onClick={() => handleDownloadTicket(b.id, b.ref)}>View Ticket</button>
                    )}
                    {b.status === "CONFIRMED" && (
                      <button className="neo-btn sm danger" onClick={() => cancel(b.id)}>Cancel</button>
                    )}
                    {b.status === "CANCELLED" && (
                      <span style={{ fontSize: 12, fontWeight: 700, color: "var(--green)" }}>Refunded ₹{b.final_amount}</span>
                    )}
                  </div>
                </div>
              </div>
            </div>
          ))}
          {bookingsList.length === 0 && <div className="neo-card text-center">No {tab.toLowerCase()} bookings.</div>}
        </div>
      )}
    </div>
  );
}
