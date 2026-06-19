import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { users as allUsers } from "../data/mockData";
import Modal from "../components/Modal";

export const Route = createFileRoute("/admin/users")({ component: AdminUsers });

function AdminUsers() {
  const [search, setSearch] = useState("");
  const [list, setList] = useState(allUsers);
  const [detail, setDetail] = useState<any>(null);

  const filtered = list.filter(u => !search || u.name.toLowerCase().includes(search.toLowerCase()) || u.email.toLowerCase().includes(search.toLowerCase()));
  const toggle = (id: string) => setList(s => s.map(u => u.id === id ? { ...u, status: u.status === "ACTIVE" ? "BLOCKED" : "ACTIVE" } : u));

  return (
    <div>
      <h1 style={{ fontSize: 32, fontWeight: 800, textTransform: "uppercase" }}>Users</h1>
      <div className="neo-card mt-4 mb-4">
        <input className="neo-input" placeholder="Search users…" value={search} onChange={e => setSearch(e.target.value)} />
      </div>
      <table className="neo-table">
        <thead><tr><th>Name</th><th>Email</th><th>Phone</th><th>Bookings</th><th>Spent</th><th>Status</th><th>Actions</th></tr></thead>
        <tbody>
          {filtered.map(u => (
            <tr key={u.id}>
              <td><b>{u.name}</b></td>
              <td>{u.email}</td>
              <td className="mono">{u.phone}</td>
              <td>{u.bookings}</td>
              <td className="mono">₹{u.totalSpent}</td>
              <td><span className={`neo-badge ${u.status === "ACTIVE" ? "green" : "coral"}`}>{u.status}</span></td>
              <td>
                <div className="flex gap-2">
                  <button className="neo-btn sm outline" onClick={() => setDetail(u)}>View</button>
                  <button className="neo-btn sm danger" onClick={() => toggle(u.id)}>{u.status === "ACTIVE" ? "Block" : "Unblock"}</button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      <Modal open={!!detail} onClose={() => setDetail(null)} title={detail?.name}>
        {detail && (
          <div>
            <p><b>Email:</b> {detail.email}</p>
            <p><b>Phone:</b> {detail.phone}</p>
            <p><b>City:</b> {detail.city}</p>
            <p><b>Role:</b> {detail.role}</p>
            <p><b>Total bookings:</b> {detail.bookings}</p>
            <p><b>Total spent:</b> ₹{detail.totalSpent}</p>
            <p><b>Wallet:</b> ₹{detail.wallet}</p>
          </div>
        )}
      </Modal>
    </div>
  );
}
