import { useState } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { useAuth } from "../context/AuthContext";

export const Route = createFileRoute("/dashboard/profile")({ component: Profile });

function Profile() {
  const { user, pushToast } = useAuth();
  const [form, setForm] = useState({ name: user?.name || "", email: user?.email || "", phone: user?.phone || "", city: user?.city || "" });
  const [showPwd, setShowPwd] = useState(false);
  const [prefs, setPrefs] = useState({ sms: true, email: true, whatsapp: false });

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }));

  return (
    <div>
      <h1 style={{ fontSize: 32, fontWeight: 800, textTransform: "uppercase" }}>Profile</h1>
      <div className="neo-card mt-4" style={{ maxWidth: 720 }}>
        <div className="flex gap-4 center mb-4">
          <div style={{ width: 80, height: 80, borderRadius: "50%", background: "var(--yellow)", border: "var(--border)", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: 28 }}>
            {form.name.split(" ").map(p => p[0]).slice(0,2).join("").toUpperCase()}
          </div>
          <button className="neo-btn sm outline">Change Photo</button>
        </div>
        <div className="form-row">
          <div className="field"><label className="neo-label">Name</label><input className="neo-input" value={form.name} onChange={e => set("name", e.target.value)} /></div>
          <div className="field"><label className="neo-label">Email</label><input className="neo-input" value={form.email} onChange={e => set("email", e.target.value)} /></div>
        </div>
        <div className="form-row">
          <div className="field"><label className="neo-label">Phone</label><input className="neo-input" value={form.phone} onChange={e => set("phone", e.target.value)} /></div>
          <div className="field"><label className="neo-label">City</label><input className="neo-input" value={form.city} onChange={e => set("city", e.target.value)} /></div>
        </div>

        <button className="neo-btn outline sm" onClick={() => setShowPwd(s => !s)}>{showPwd ? "Hide" : "Change"} password</button>
        {showPwd && (
          <div className="mt-4">
            <div className="form-row">
              <input className="neo-input" type="password" placeholder="Current password" />
              <input className="neo-input" type="password" placeholder="New password" />
            </div>
          </div>
        )}

        <h3 className="section-title mt-8" style={{ fontSize: 18 }}>Notifications</h3>
        <div style={{ display: "grid", gap: 8 }}>
          {(["sms","email","whatsapp"] as const).map(k => (
            <label key={k} className="flex between center" style={{ padding: 10, border: "2px solid var(--ink)", background: "var(--white)" }}>
              <span style={{ textTransform: "uppercase", fontWeight: 700, fontSize: 13 }}>{k}</span>
              <input type="checkbox" checked={prefs[k]} onChange={e => setPrefs(p => ({ ...p, [k]: e.target.checked }))} />
            </label>
          ))}
        </div>

        <div className="flex gap-3 mt-6">
          <button className="neo-btn" onClick={() => pushToast("Profile saved!", "success")}>Save Changes</button>
          <button className="neo-btn danger">Delete Account</button>
        </div>
      </div>
    </div>
  );
}
