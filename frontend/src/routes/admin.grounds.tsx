import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { grounds as initial } from "../data/mockData";
import Modal from "../components/Modal";
import { useAuth } from "../context/AuthContext";

export const Route = createFileRoute("/admin/grounds")({ component: AdminGrounds });

function AdminGrounds() {
  const { pushToast } = useAuth();
  const [list, setList] = useState(initial.map(g => ({ ...g, active: true })));
  const [open, setOpen] = useState(false);

  const toggle = (id: string) => setList(s => s.map(g => g.id === id ? { ...g, active: !g.active } : g));
  const remove = (id: string) => { setList(s => s.filter(g => g.id !== id)); pushToast("Ground deleted", "success"); };

  return (
    <div>
      <div className="flex between center">
        <h1 style={{ fontSize: 32, fontWeight: 800, textTransform: "uppercase" }}>Grounds</h1>
        <button className="neo-btn" onClick={() => setOpen(true)}>+ Add Ground</button>
      </div>
      <table className="neo-table mt-4">
        <thead><tr><th>Name</th><th>Location</th><th>Slots/day</th><th>Price</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>
          {list.map(g => (
            <tr key={g.id}>
              <td><b>{g.name}</b></td>
              <td>{g.location}</td>
              <td>{g.totalSlots}</td>
              <td className="mono">₹{g.price}</td>
              <td><label><input type="checkbox" checked={g.active} onChange={() => toggle(g.id)} /> {g.active ? "ACTIVE" : "INACTIVE"}</label></td>
              <td>
                <div className="flex gap-2">
                  <button className="neo-btn sm outline">Edit</button>
                  <button className="neo-btn sm secondary">Slots</button>
                  <button className="neo-btn sm danger" onClick={() => remove(g.id)}>Delete</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <Modal open={open} onClose={() => setOpen(false)} title="Add Ground">
        <div className="field"><label className="neo-label">Name</label><input className="neo-input" /></div>
        <div className="field"><label className="neo-label">Location</label><input className="neo-input" /></div>
        <div className="field"><label className="neo-label">Description</label><textarea className="neo-input" rows={3}></textarea></div>
        <div className="form-row">
          <div className="field"><label className="neo-label">Price/hr</label><input className="neo-input" type="number" /></div>
          <div className="field"><label className="neo-label">Capacity</label><input className="neo-input" type="number" /></div>
        </div>
        <div className="form-row">
          <div className="field"><label className="neo-label">Opening</label><input className="neo-input" type="time" /></div>
          <div className="field"><label className="neo-label">Closing</label><input className="neo-input" type="time" /></div>
        </div>
        <label className="neo-label">Amenities</label>
        <div className="flex gap-3 mb-4" style={{ flexWrap: "wrap" }}>
          {["Floodlights","Parking","Changing Room","Cafeteria","Live Scoring"].map(a => (
            <label key={a} style={{ fontSize: 13 }}><input type="checkbox" /> {a}</label>
          ))}
        </div>
        <button className="neo-btn block" onClick={() => { setOpen(false); pushToast("Ground saved!", "success"); }}>Save Ground</button>
      </Modal>
    </div>
  );
}
