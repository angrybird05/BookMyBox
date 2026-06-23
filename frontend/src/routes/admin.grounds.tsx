import { useState, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { apiGetGrounds, apiAdminCreateGround, apiAdminToggleGroundStatus, apiAdminDeleteGround } from "../lib/api";
import Modal from "../components/Modal";
import { useAuth } from "../context/AuthContext";

export const Route = createFileRoute("/admin/grounds")({ component: AdminGrounds });

function AdminGrounds() {
  const { pushToast } = useAuth();
  const [list, setList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [open, setOpen] = useState(false);

  // New ground form states
  const [name, setName] = useState("");
  const [location, setLocation] = useState("");
  const [description, setDescription] = useState("");
  const [price, setPrice] = useState("");
  const [openTime, setOpenTime] = useState("06:00");
  const [closeTime, setCloseTime] = useState("23:00");
  const [amenities, setAmenities] = useState<string[]>([]);

  const fetchGrounds = async () => {
    setLoading(true);
    try {
      const res = await apiGetGrounds({ per_page: 50 });
      setList(res.data || []);
    } catch (err: any) {
      pushToast(err.message || "Failed to load grounds", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchGrounds();
  }, []);

  const toggle = async (id: string, currentStatus: boolean) => {
    try {
      const updated = await apiAdminToggleGroundStatus(id, !currentStatus);
      pushToast(`Ground status updated!`, "success");
      fetchGrounds();
    } catch (err: any) {
      pushToast(err.message || "Failed to update ground status", "error");
    }
  };

  const remove = async (id: string) => {
    if (!confirm("Are you sure you want to delete this ground?")) return;
    try {
      await apiAdminDeleteGround(id);
      pushToast("Ground deleted successfully", "success");
      fetchGrounds();
    } catch (err: any) {
      pushToast(err.message || "Failed to delete ground", "error");
    }
  };

  const toggleAmenity = (a: string) => {
    setAmenities(prev => prev.includes(a) ? prev.filter(x => x !== a) : [...prev, a]);
  };

  const handleSaveGround = async () => {
    if (!name || !location || !price) {
      pushToast("Name, location and price are required", "error");
      return;
    }
    try {
      await apiAdminCreateGround({
        name,
        location,
        city: "Hyderabad", // default city
        description,
        price_per_hour: parseInt(price),
        amenities,
        open_time: openTime,
        close_time: closeTime,
        slot_duration_minutes: 60,
        gradient: "linear-gradient(135deg,#FFE500,#FF6B6B)", // default gradients
        icon: "🏏"
      });
      pushToast("Ground created successfully!", "success");
      setOpen(false);
      
      // Reset form
      setName("");
      setLocation("");
      setDescription("");
      setPrice("");
      setAmenities([]);
      
      fetchGrounds();
    } catch (err: any) {
      pushToast(err.message || "Failed to create ground", "error");
    }
  };

  return (
    <div>
      <div className="flex between center">
        <h1 style={{ fontSize: 32, fontWeight: 800, textTransform: "uppercase" }}>Grounds</h1>
        <button className="neo-btn" onClick={() => setOpen(true)}>+ Add Ground</button>
      </div>

      {loading ? (
        <div className="neo-card text-center mt-4" style={{ padding: 40 }}>Loading grounds...</div>
      ) : (
        <table className="neo-table mt-4">
          <thead><tr><th>Name</th><th>Location</th><th>Slots/day</th><th>Price</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            {list.map(g => (
              <tr key={g.id}>
                <td><b>{g.name}</b></td>
                <td>{g.location}</td>
                <td>{g.total_slots || 16}</td>
                <td className="mono">₹{g.price_per_hour}</td>
                <td>
                  <label>
                    <input type="checkbox" checked={g.is_active} onChange={() => toggle(g.id, g.is_active)} /> 
                    {g.is_active ? " ACTIVE" : " INACTIVE"}
                  </label>
                </td>
                <td>
                  <div className="flex gap-2">
                    <button className="neo-btn sm danger" onClick={() => remove(g.id)}>Delete</button>
                  </div>
                </td>
              </tr>
            ))}
            {list.length === 0 && (
              <tr>
                <td colSpan={6} className="text-center" style={{ padding: 20 }}>No grounds registered yet.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}

      <Modal open={open} onClose={() => setOpen(false)} title="Add Ground">
        <div className="field"><label className="neo-label">Name</label><input className="neo-input" value={name} onChange={e => setName(e.target.value)} /></div>
        <div className="field"><label className="neo-label">Location</label><input className="neo-input" value={location} onChange={e => setLocation(e.target.value)} /></div>
        <div className="field"><label className="neo-label">Description</label><textarea className="neo-input" rows={3} value={description} onChange={e => setDescription(e.target.value)}></textarea></div>
        <div className="form-row">
          <div className="field"><label className="neo-label">Price/hr</label><input className="neo-input" type="number" value={price} onChange={e => setPrice(e.target.value)} /></div>
        </div>
        <div className="form-row">
          <div className="field"><label className="neo-label">Opening</label><input className="neo-input" type="time" value={openTime} onChange={e => setOpenTime(e.target.value)} /></div>
          <div className="field"><label className="neo-label">Closing</label><input className="neo-input" type="time" value={closeTime} onChange={e => setCloseTime(e.target.value)} /></div>
        </div>
        <label className="neo-label">Amenities</label>
        <div className="flex gap-3 mb-4" style={{ flexWrap: "wrap" }}>
          {["Floodlights","Parking","Changing Room","Cafeteria","Live Scoring"].map(a => (
            <label key={a} style={{ fontSize: 13 }}>
              <input type="checkbox" checked={amenities.includes(a)} onChange={() => toggleAmenity(a)} /> {a}
            </label>
          ))}
        </div>
        <button className="neo-btn block" onClick={handleSaveGround}>Save Ground</button>
      </Modal>
    </div>
  );
}
