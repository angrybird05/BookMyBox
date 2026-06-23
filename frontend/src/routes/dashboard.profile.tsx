import { useState, useEffect } from "react";
import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { useAuth } from "../context/AuthContext";
import { apiUpdateMe, apiTopUpWallet, apiGetWalletBalance } from "../lib/api";

export const Route = createFileRoute("/dashboard/profile")({ component: Profile });

function Profile() {
  const { user, pushToast, logout } = useAuth();
  const navigate = useNavigate();

  const [form, setForm] = useState({ name: user?.name || "", email: user?.email || "", phone: user?.phone || "", city: user?.city || "" });
  const [showPwd, setShowPwd] = useState(false);
  const [oldPassword, setOldPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  
  // Wallet top-up
  const [topUpAmount, setTopUpAmount] = useState("");
  const [walletBalance, setWalletBalance] = useState<number | null>(null);
  
  const [prefs, setPrefs] = useState({ sms: true, email: true, whatsapp: false });

  useEffect(() => {
    if (user) {
      setForm({ name: user.name || "", email: user.email || "", phone: user.phone || "", city: user.city || "" });
      if (user.notification_prefs) {
        setPrefs({
          sms: !!user.notification_prefs.sms,
          email: !!user.notification_prefs.email,
          whatsapp: !!user.notification_prefs.whatsapp || false
        });
      }
      
      // Load current wallet balance
      async function loadWallet() {
        try {
          const w = await apiGetWalletBalance();
          setWalletBalance(w.balance);
        } catch {}
      }
      loadWallet();
    }
  }, [user]);

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }));

  const handleSaveProfile = async () => {
    try {
      await apiUpdateMe({
        name: form.name,
        phone: form.phone,
        city: form.city
      });
      pushToast("Profile details updated successfully!", "success");
    } catch (err: any) {
      pushToast(err.message || "Failed to update profile", "error");
    }
  };

  const handleTopUp = async () => {
    const amt = parseFloat(topUpAmount);
    if (isNaN(amt) || amt <= 0) {
      pushToast("Please enter a valid positive amount", "error");
      return;
    }
    try {
      const res = await apiTopUpWallet(amt);
      setWalletBalance(res.balance);
      setTopUpAmount("");
      pushToast(`Successfully added ₹${amt} to your wallet!`, "success");
    } catch (err: any) {
      pushToast(err.message || "Top-up failed", "error");
    }
  };

  const handleDeleteAccount = async () => {
    if (!confirm("WARNING: Are you sure you want to permanently delete your account? This action cannot be undone.")) return;
    try {
      // Direct fetch call since we delete current session
      const token = localStorage.getItem("bmb_access_token");
      await fetch("http://localhost:8000/api/v1/users/me", {
        method: "DELETE",
        headers: { "Authorization": `Bearer ${token}` }
      });
      pushToast("Account deleted successfully.", "info");
      logout();
      navigate({ to: "/" });
    } catch (err: any) {
      pushToast(err.message || "Deletion failed", "error");
    }
  };

  if (!user) return null;

  return (
    <div>
      <h1 style={{ fontSize: 32, fontWeight: 800, textTransform: "uppercase" }}>Profile & Settings</h1>
      
      <div className="detail-layout mt-4">
        <div className="neo-card" style={{ maxWidth: 720 }}>
          <div className="flex gap-4 center mb-4">
            <div style={{ width: 80, height: 80, borderRadius: "50%", background: "var(--yellow)", border: "var(--border)", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: 28 }}>
              {form.name.split(" ").map(p => p[0]).slice(0,2).join("").toUpperCase()}
            </div>
            <div className="mono" style={{ fontSize: 14 }}>{user.role?.toUpperCase()}</div>
          </div>
          <div className="form-row">
            <div className="field"><label className="neo-label">Name</label><input className="neo-input" value={form.name} onChange={e => set("name", e.target.value)} /></div>
            <div className="field"><label className="neo-label">Email</label><input className="neo-input" disabled value={form.email} style={{ background: "#eee", cursor: "not-allowed" }} /></div>
          </div>
          <div className="form-row">
            <div className="field"><label className="neo-label">Phone</label><input className="neo-input" value={form.phone} onChange={e => set("phone", e.target.value)} /></div>
            <div className="field"><label className="neo-label">City</label><input className="neo-input" value={form.city} onChange={e => set("city", e.target.value)} /></div>
          </div>

          <h3 className="section-title mt-8" style={{ fontSize: 18 }}>Notifications</h3>
          <div style={{ display: "grid", gap: 8 }}>
            {(["sms","email","whatsapp"] as const).map(k => (
              <label key={k} className="flex between center" style={{ padding: 10, border: "2px solid var(--ink)", background: "var(--white)" }}>
                <span style={{ textTransform: "uppercase", fontWeight: 700, fontSize: 13 }}>{k}</span>
                <input type="checkbox" checked={prefs[k]} onChange={e => setPrefs(p => ({ ...p, [k]: e.target.checked }))} />
              </label>
            ))}
          </div>

          <div className="flex gap-3 mt-6" style={{ flexWrap: "wrap" }}>
            <button className="neo-btn" onClick={handleSaveProfile}>Save Changes</button>
            <button className="neo-btn danger" onClick={handleDeleteAccount}>Delete Account</button>
          </div>
        </div>

        <div className="booking-widget">
          <div className="neo-card mb-4">
            <h3 style={{ textTransform: "uppercase", fontWeight: 800, marginBottom: 12 }}>My Wallet</h3>
            <div className="mono mb-4" style={{ fontSize: 32, fontWeight: 700 }}>
              ₹{walletBalance !== null ? walletBalance : "Loading..."}
            </div>
            <label className="neo-label">Top-up Wallet</label>
            <div className="flex gap-2">
              <input className="neo-input" type="number" placeholder="Enter amount (₹)" value={topUpAmount} onChange={e => setTopUpAmount(e.target.value)} />
              <button className="neo-btn sm" onClick={handleTopUp}>Add</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
