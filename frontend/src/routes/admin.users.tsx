import { useState, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { apiAdminGetUsers, apiAdminToggleUserBlock } from "../lib/api";
import Modal from "../components/Modal";
import { useAuth } from "../context/AuthContext";

export const Route = createFileRoute("/admin/users")({ component: AdminUsers });

function AdminUsers() {
  const { pushToast } = useAuth();
  const [search, setSearch] = useState("");
  const [list, setList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [detail, setDetail] = useState<any>(null);

  const fetchUsers = async () => {
    setLoading(true);
    try {
      const res = await apiAdminGetUsers(search || undefined);
      setList(res.data || []);
    } catch (err: any) {
      pushToast(err.message || "Failed to load users", "error");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [search]);

  const toggle = async (id: string, currentStatus: string) => {
    const nextStatus = currentStatus === "ACTIVE" ? "BLOCKED" : "ACTIVE";
    try {
      await apiAdminToggleUserBlock(id, nextStatus);
      pushToast(`User status updated to ${nextStatus}`, "success");
      fetchUsers();
    } catch (err: any) {
      pushToast(err.message || "Failed to update user status", "error");
    }
  };

  return (
    <div>
      <h1 style={{ fontSize: 32, fontWeight: 800, textTransform: "uppercase" }}>Users</h1>
      <div className="neo-card mt-4 mb-4">
        <input className="neo-input" placeholder="Search users…" value={search} onChange={e => setSearch(e.target.value)} />
      </div>
      
      {loading ? (
        <div className="neo-card text-center" style={{ padding: 40 }}>Loading users...</div>
      ) : (
        <table className="neo-table">
          <thead><tr><th>Name</th><th>Email</th><th>Phone</th><th>Role</th><th>Status</th><th>Actions</th></tr></thead>
          <tbody>
            {list.map(u => (
              <tr key={u.id}>
                <td><b>{u.name}</b></td>
                <td>{u.email}</td>
                <td className="mono">{u.phone}</td>
                <td>{u.role}</td>
                <td><span className={`neo-badge ${u.status === "ACTIVE" ? "green" : "coral"}`}>{u.status}</span></td>
                <td>
                  <div className="flex gap-2">
                    <button className="neo-btn sm outline" onClick={() => setDetail(u)}>View</button>
                    <button className="neo-btn sm danger" onClick={() => toggle(u.id, u.status)}>
                      {u.status === "ACTIVE" ? "Block" : "Unblock"}
                    </button>
                  </div>
                </td>
              </tr>
            ))}
            {list.length === 0 && (
              <tr>
                <td colSpan={6} className="text-center" style={{ padding: 20 }}>No users found.</td>
              </tr>
            )}
          </tbody>
        </table>
      )}

      <Modal open={!!detail} onClose={() => setDetail(null)} title={detail?.name}>
        {detail && (
          <div>
            <p><b>Email:</b> {detail.email}</p>
            <p><b>Phone:</b> {detail.phone}</p>
            <p><b>City:</b> {detail.city || "Not specified"}</p>
            <p><b>Role:</b> {detail.role}</p>
            <p><b>Status:</b> {detail.status}</p>
          </div>
        )}
      </Modal>
    </div>
  );
}
