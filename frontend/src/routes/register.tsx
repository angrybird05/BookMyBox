import { useState, type FormEvent } from "react";
import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useAuth } from "../context/AuthContext";

export const Route = createFileRoute("/register")({ component: Register });

function Register() {
  const { register, pushToast } = useAuth();
  const navigate = useNavigate();
  const [role, setRole] = useState<"user" | "admin">("user");
  const [form, setForm] = useState({
    name: "",
    email: "",
    phone: "",
    password: "",
    confirm: "",
    city: "Hyderabad",
    groundName: ""
  });
  const [errors, setErrors] = useState<Record<string, string>>({});
  const [otpStep, setOtpStep] = useState(false);
  const [otp, setOtp] = useState("");
  const [focusedField, setFocusedField] = useState<string | null>(null);

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }));

  const handleRoleChange = (newRole: "user" | "admin") => {
    setRole(newRole);
    setErrors({});
    setForm({
      name: "",
      email: "",
      phone: "",
      password: "",
      confirm: "",
      city: "Hyderabad",
      groundName: ""
    });
  };

  const getFocusStyle = (fieldName: string) => {
    return {
      boxShadow: focusedField === fieldName ? `4px 4px 0 ${role === "user" ? "var(--yellow)" : "var(--purple)"}` : "none",
      transition: "all 0.1s ease"
    };
  };

  const submit = (e: FormEvent) => {
    e.preventDefault();
    const errs: Record<string, string> = {};
    if (!form.name.trim()) errs.name = "Name is required";
    if (!form.email.includes("@")) errs.email = "Valid email is required";
    if (form.phone.trim().length < 10) errs.phone = "Valid phone is required (min 10 digits)";
    if (role === "admin" && !form.groundName.trim()) errs.groundName = "Turf / Business Name is required";
    if (form.password.length < 6) errs.password = "Password must be at least 6 characters";
    if (form.password !== form.confirm) errs.confirm = "Passwords do not match";
    
    setErrors(errs);
    if (Object.keys(errs).length) return;
    
    setOtpStep(true);
    pushToast("OTP sent to your phone (use 123456)", "info");
  };

  const verifyOtp = (e: FormEvent) => {
    e.preventDefault();
    if (otp !== "123456") { setErrors({ otp: "Invalid OTP. Try 123456" }); return; }
    
    const res = register({
      name: form.name,
      email: form.email,
      phone: form.phone,
      password: form.password,
      role: role,
      city: role === "user" ? form.city : "",
      groundName: role === "admin" ? form.groundName : ""
    });
    
    if (!res.ok) { setErrors({ otp: res.error || "Registration failed" }); return; }
    pushToast("Account created successfully!", "success");
    navigate({ to: res.user.role === "admin" ? "/admin" : "/dashboard" });
  };

  const quickFill = (selectedRole: "user" | "admin") => {
    setRole(selectedRole);
    setErrors({});
    if (selectedRole === "user") {
      setForm({
        name: "Rohit Sharma",
        email: "rohit.player@test.com",
        phone: "9876543210",
        password: "password123",
        confirm: "password123",
        city: "Hyderabad",
        groundName: ""
      });
    } else {
      setForm({
        name: "Kunal Kapoor",
        email: "kunal.admin@test.com",
        phone: "9900112233",
        password: "password123",
        confirm: "password123",
        city: "",
        groundName: "Sixer Turf Arena"
      });
    }
    pushToast(`Autofilled demo ${selectedRole === "user" ? "Player" : "Partner"} details!`, "info");
  };

  return (
    <div className="auth-wrap" style={{ background: "radial-gradient(var(--light) 20%, transparent 20%)", backgroundSize: "16px 16px" }}>
      <div className="auth-card" style={{ position: "relative", overflow: "hidden" }}>
        {/* Dynamic header colored bar accent */}
        <div style={{
          height: "12px",
          background: role === "user" ? "var(--yellow)" : "var(--purple)",
          borderBottom: "var(--border)",
          margin: "-32px -32px 24px -32px",
          transition: "background 0.25s ease"
        }}></div>

        <div className="flex between center mb-4">
          <h1 style={{ fontSize: 24, margin: 0 }}>
            {otpStep ? "Verify OTP" : "Create Account"}
          </h1>
          <span className="neo-badge dark" style={{
            background: role === "user" ? "var(--yellow)" : "var(--purple)",
            color: "var(--ink)",
            transition: "all 0.25s ease"
          }}>
            {role === "user" ? "🏏 PLAYER" : "👑 PARTNER"}
          </span>
        </div>

        {!otpStep ? (
          <>
            <p style={{ fontSize: 13, marginBottom: 20, color: "#555" }}>
              {role === "user"
                ? "Join as a Player to search venues, checkout multiple slots, and track bookings."
                : "Register as a Turf Partner to list your grounds, view bookings, and manage schedules."}
            </p>

            {/* Neo-brutalist Tab Switcher */}
            <div style={{ display: "flex", gap: "10px", marginBottom: "24px" }}>
              <button
                type="button"
                onClick={() => handleRoleChange("user")}
                className="neo-btn sm"
                style={{
                  flex: 1,
                  background: role === "user" ? "var(--yellow)" : "var(--white)",
                  boxShadow: role === "user" ? "var(--shadow)" : "none",
                  transform: role === "user" ? "translate(-2px, -2px)" : "none",
                  border: "var(--border)",
                  transition: "all 0.15s ease"
                }}
              >
                🏏 Join as Player
              </button>
              <button
                type="button"
                onClick={() => handleRoleChange("admin")}
                className="neo-btn sm"
                style={{
                  flex: 1,
                  background: role === "admin" ? "var(--purple)" : "var(--white)",
                  boxShadow: role === "admin" ? "var(--shadow)" : "none",
                  transform: role === "admin" ? "translate(-2px, -2px)" : "none",
                  border: "var(--border)",
                  transition: "all 0.15s ease"
                }}
              >
                👑 Join as Partner
              </button>
            </div>

            <form onSubmit={submit}>
              <div className="field">
                <label className="neo-label">Full Name</label>
                <input
                  className="neo-input"
                  value={form.name}
                  onChange={e => set("name", e.target.value)}
                  onFocus={() => setFocusedField("name")}
                  onBlur={() => setFocusedField(null)}
                  style={getFocusStyle("name")}
                />
                {errors.name && <div className="neo-error">{errors.name}</div>}
              </div>

              <div className="field">
                <label className="neo-label">Email Address</label>
                <input
                  className="neo-input"
                  type="email"
                  value={form.email}
                  onChange={e => set("email", e.target.value)}
                  onFocus={() => setFocusedField("email")}
                  onBlur={() => setFocusedField(null)}
                  style={getFocusStyle("email")}
                />
                {errors.email && <div className="neo-error">{errors.email}</div>}
              </div>

              <div className="field">
                <label className="neo-label">Phone Number</label>
                <input
                  className="neo-input"
                  value={form.phone}
                  onChange={e => set("phone", e.target.value)}
                  onFocus={() => setFocusedField("phone")}
                  onBlur={() => setFocusedField(null)}
                  style={getFocusStyle("phone")}
                />
                {errors.phone && <div className="neo-error">{errors.phone}</div>}
              </div>

              {/* Dynamic role-specific fields */}
              {role === "user" ? (
                <div className="field">
                  <label className="neo-label">City</label>
                  <select
                    className="neo-input"
                    value={form.city}
                    onChange={e => set("city", e.target.value)}
                    onFocus={() => setFocusedField("city")}
                    onBlur={() => setFocusedField(null)}
                    style={getFocusStyle("city")}
                  >
                    <option value="Hyderabad">Hyderabad</option>
                    <option value="Bengaluru">Bengaluru</option>
                    <option value="Mumbai">Mumbai</option>
                    <option value="Delhi">Delhi</option>
                  </select>
                </div>
              ) : (
                <div className="field">
                  <label className="neo-label">Turf / Business Name</label>
                  <input
                    className="neo-input"
                    placeholder="e.g. Boundary Hitters Arena"
                    value={form.groundName}
                    onChange={e => set("groundName", e.target.value)}
                    onFocus={() => setFocusedField("groundName")}
                    onBlur={() => setFocusedField(null)}
                    style={getFocusStyle("groundName")}
                  />
                  {errors.groundName && <div className="neo-error">{errors.groundName}</div>}
                </div>
              )}

              <div className="field">
                <label className="neo-label">Password</label>
                <input
                  className="neo-input"
                  type="password"
                  value={form.password}
                  onChange={e => set("password", e.target.value)}
                  onFocus={() => setFocusedField("password")}
                  onBlur={() => setFocusedField(null)}
                  style={getFocusStyle("password")}
                />
                {errors.password && <div className="neo-error">{errors.password}</div>}
              </div>

              <div className="field">
                <label className="neo-label">Confirm Password</label>
                <input
                  className="neo-input"
                  type="password"
                  value={form.confirm}
                  onChange={e => set("confirm", e.target.value)}
                  onFocus={() => setFocusedField("confirm")}
                  onBlur={() => setFocusedField(null)}
                  style={getFocusStyle("confirm")}
                />
                {errors.confirm && <div className="neo-error">{errors.confirm}</div>}
              </div>

              <button
                className="neo-btn block lg"
                type="submit"
                style={{
                  background: role === "user" ? "var(--yellow)" : "var(--purple)",
                  transition: "background 0.2s ease"
                }}
              >
                Register as {role === "user" ? "Player" : "Partner"} →
              </button>
            </form>
          </>
        ) : (
          <form onSubmit={verifyOtp}>
            <p className="mb-4" style={{ fontSize: 14 }}>
              We've sent a 6-digit verification code to <b>{form.phone}</b>.
            </p>
            <div className="field">
              <label className="neo-label">Enter OTP Code</label>
              <input
                className="neo-input mb-2"
                placeholder="Enter Code (use 123456)"
                value={otp}
                onChange={e => setOtp(e.target.value)}
                onFocus={() => setFocusedField("otp")}
                onBlur={() => setFocusedField(null)}
                style={getFocusStyle("otp")}
              />
              {errors.otp && <div className="neo-error mb-4">{errors.otp}</div>}
            </div>
            <button
              className="neo-btn block lg"
              type="submit"
              style={{
                background: role === "user" ? "var(--yellow)" : "var(--purple)",
                transition: "background 0.2s ease"
              }}
            >
              Verify & Complete Registration →
            </button>
            <button
              type="button"
              className="neo-btn block outline mt-2"
              onClick={() => setOtpStep(false)}
            >
              ← Back to Registration Form
            </button>
          </form>
        )}

        <div className="mt-4 text-center" style={{ fontSize: 13 }}>
          Already have an account?{" "}
          <Link to="/login" style={{ fontWeight: 700, textDecoration: "underline" }}>
            Login →
          </Link>
        </div>

        {/* Demo Autofill console */}
        {!otpStep && (
          <div style={{ marginTop: 24, padding: 16, background: "var(--light)", border: "2px solid var(--ink)", boxShadow: "var(--shadow-sm)" }}>
            <div style={{ fontSize: 11, fontFamily: "var(--mono)", fontWeight: 700, textTransform: "uppercase", marginBottom: 12, borderBottom: "2px dashed var(--ink)", paddingBottom: 6 }}>
              🛠️ Demo Autofill Console
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "10px" }}>
              <button
                type="button"
                className="neo-btn outline sm"
                onClick={() => quickFill("user")}
                style={{ fontSize: 11 }}
              >
                🏏 Fill Player Form
              </button>
              <button
                type="button"
                className="neo-btn outline sm"
                onClick={() => quickFill("admin")}
                style={{ fontSize: 11 }}
              >
                👑 Fill Partner Form
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
