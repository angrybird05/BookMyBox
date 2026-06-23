import { useState, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { apiGetGrounds, apiAdminGetSlots, apiAdminBlockSlots, apiAdminUnblockSlots, apiAdminBulkUpdateSlotPrices } from "../lib/api";
import { useAuth } from "../context/AuthContext";

export const Route = createFileRoute("/admin/slots")({ component: AdminSlots });

function AdminSlots() {
  const { pushToast } = useAuth();
  const [groundsList, setGroundsList] = useState<any[]>([]);
  const [groundId, setGroundId] = useState("");
  const [date, setDate] = useState(new Date().toISOString().slice(0, 10));
  const [slots, setSlots] = useState<any[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedSlotIds, setSelectedSlotIds] = useState<string[]>([]);
  const [priceInput, setPriceInput] = useState("");

  // Load grounds list
  useEffect(() => {
    async function loadGrounds() {
      try {
        const res = await apiGetGrounds({ per_page: 50 });
        setGroundsList(res.data || []);
        if (res.data && res.data.length > 0) {
          setGroundId(res.data[0].id);
        }
      } catch (err) {
        console.error("Failed to load grounds list", err);
      }
    }
    loadGrounds();
  }, []);

  const fetchSlots = async () => {
    if (!groundId || !date) return;
    setLoading(true);
    try {
      const res = await apiAdminGetSlots(groundId, date);
      if (res && res.data) {
        const normalized = res.data.map((s: any) => ({
          id: s.id,
          startTime: s.start_time,
          endTime: s.end_time,
          price: s.price,
          status: s.status, // AVAILABLE, BOOKED, BLOCKED
        }));
        setSlots(normalized);
        setSelectedSlotIds([]);
      }
    } catch (err: any) {
      pushToast(err.message || "Failed to load slots", "error");
    } finally {
      setLoading(false);
    }
  };

  // Load slots when ground or date changes
  useEffect(() => {
    fetchSlots();
  }, [groundId, date]);

  const toggleSelectSlot = (id: string) => {
    setSelectedSlotIds(prev =>
      prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]
    );
  };

  const blockSelected = async () => {
    if (selectedSlotIds.length === 0) {
      pushToast("Select one or more slots first", "error");
      return;
    }
    try {
      await apiAdminBlockSlots(selectedSlotIds);
      pushToast("Slots blocked successfully", "success");
      fetchSlots();
    } catch (err: any) {
      pushToast(err.message || "Failed to block slots", "error");
    }
  };

  const unblockSelected = async () => {
    if (selectedSlotIds.length === 0) {
      pushToast("Select one or more slots first", "error");
      return;
    }
    try {
      await apiAdminUnblockSlots(selectedSlotIds);
      pushToast("Slots unblocked successfully", "success");
      fetchSlots();
    } catch (err: any) {
      pushToast(err.message || "Failed to unblock slots", "error");
    }
  };

  const updatePrice = async () => {
    if (selectedSlotIds.length === 0) {
      pushToast("Select one or more slots first", "error");
      return;
    }
    const price = parseInt(priceInput);
    if (isNaN(price) || price < 0) {
      pushToast("Please enter a valid positive price", "error");
      return;
    }
    try {
      await apiAdminBulkUpdateSlotPrices(selectedSlotIds, price);
      pushToast("Slot prices updated successfully", "success");
      setPriceInput("");
      fetchSlots();
    } catch (err: any) {
      pushToast(err.message || "Failed to update prices", "error");
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: 32, fontWeight: 800, textTransform: "uppercase" }}>Slot Management</h1>
      <div className="neo-card mt-4">
        <div className="form-row">
          <div className="field">
            <label className="neo-label">Ground</label>
            <select className="neo-input" value={groundId} onChange={e => setGroundId(e.target.value)}>
              {groundsList.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
            </select>
          </div>
          <div className="field"><label className="neo-label">Date</label><input className="neo-input" type="date" value={date} onChange={e => setDate(e.target.value)} /></div>
        </div>
        
        <div className="flex gap-3 mb-4 mt-4" style={{ flexWrap: "wrap", alignItems: "center" }}>
          <button className="neo-btn sm danger" onClick={blockSelected}>Block Selected</button>
          <button className="neo-btn sm secondary" onClick={unblockSelected}>Unblock Selected</button>
          <div className="flex gap-2" style={{ alignItems: "center" }}>
            <input className="neo-input" type="number" placeholder="New Price (₹)" value={priceInput} onChange={e => setPriceInput(e.target.value)} style={{ width: 140, marginBottom: 0 }} />
            <button className="neo-btn sm" onClick={updatePrice}>Set Price</button>
          </div>
        </div>

        {loading ? (
          <div className="text-center py-8">Loading slots...</div>
        ) : (
          <div className="slot-grid">
            {slots.map(s => {
              const isSelected = selectedSlotIds.includes(s.id);
              const cls = ["slot", s.status === "BOOKED" ? "booked" : s.status === "BLOCKED" ? "blocked" : "", isSelected ? "selected" : ""].join(" ");
              return (
                <button key={s.id} className={cls} disabled={s.status === "BOOKED"} onClick={() => toggleSelectSlot(s.id)} style={s.status === "BLOCKED" ? { background: "#ffccd5" } : undefined}>
                  <span className="t">{s.startTime}–{s.endTime}</span>
                  <span className="p">{s.status === "BOOKED" ? "BOOKED" : s.status === "BLOCKED" ? "BLOCKED" : "AVAILABLE"} • ₹{s.price}</span>
                </button>
              );
            })}
            {slots.length === 0 && <div className="text-center py-4 w-full">No operating hours defined for this ground.</div>}
          </div>
        )}
      </div>
    </div>
  );
}
