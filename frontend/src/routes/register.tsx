import { useState, type FormEvent } from "react";
import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useAuth } from "../context/AuthContext";

export const Route = createFileRoute("/register")({ component: Register });

function Register() {
  const { register, pushToast } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ name: "", email: "", phone: "", password: "", confirm: "" });
  const [errors, setErrors] = useState<Record<string,string>>({});
  const [otpStep, setOtpStep] = useState(false);
  const [otp, setOtp] = useState("");

  const set = (k: string, v: string) => setForm(f => ({ ...f, [k]: v }));

  const submit = (e: FormEvent) => {
    e.preventDefault();
    const errs: Record<string,string> = {};
    if (!form.name) errs.name = "Name required";
    if (!form.email.includes("@")) errs.email = "Valid email required";
    if (form.phone.length < 10) errs.phone = "Valid phone required";
    if (form.password.length < 6) errs.password = "Min 6 characters";
    if (form.password !== form.confirm) errs.confirm = "Passwords don't match";
    setErrors(errs);
    if (Object.keys(errs).length) return;
    setOtpStep(true);
    pushToast("OTP sent to your phone (use 123456)", "info");
  };

  const verifyOtp = (e: FormEvent) => {
    e.preventDefault();
    if (otp !== "123456") { setErrors({ otp: "Invalid OTP. Try 123456" }); return; }
    const res = register({ name: form.name, email: form.email, phone: form.phone, password: form.password, city: "" });
    if (!res.ok) { setErrors({ otp: res.error || "Error" }); return; }
    pushToast("Account created!", "success");
    navigate({ to: "/dashboard" });
  };

  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <h1>{otpStep ? "Verify OTP" : "Create Account"}</h1>
        {!otpStep ? (
          <form onSubmit={submit}>
            <div className="field"><label className="neo-label">Name</label><input className="neo-input" value={form.name} onChange={e => set("name", e.target.value)} />{errors.name && <div className="neo-error">{errors.name}</div>}</div>
            <div className="field"><label className="neo-label">Email</label><input className="neo-input" value={form.email} onChange={e => set("email", e.target.value)} />{errors.email && <div className="neo-error">{errors.email}</div>}</div>
            <div className="field"><label className="neo-label">Phone</label><input className="neo-input" value={form.phone} onChange={e => set("phone", e.target.value)} />{errors.phone && <div className="neo-error">{errors.phone}</div>}</div>
            <div className="field"><label className="neo-label">Password</label><input className="neo-input" type="password" value={form.password} onChange={e => set("password", e.target.value)} />{errors.password && <div className="neo-error">{errors.password}</div>}</div>
            <div className="field"><label className="neo-label">Confirm Password</label><input className="neo-input" type="password" value={form.confirm} onChange={e => set("confirm", e.target.value)} />{errors.confirm && <div className="neo-error">{errors.confirm}</div>}</div>
            <button className="neo-btn block lg" type="submit">Create Account →</button>
          </form>
        ) : (
          <form onSubmit={verifyOtp}>
            <p className="mb-4">We've sent a 6-digit OTP to {form.phone}.</p>
            <input className="neo-input mb-4" placeholder="Enter OTP" value={otp} onChange={e => setOtp(e.target.value)} />
            {errors.otp && <div className="neo-error mb-4">{errors.otp}</div>}
            <button className="neo-btn block lg" type="submit">Verify & Continue →</button>
          </form>
        )}
        <div className="mt-4 text-center" style={{ fontSize: 13 }}>
          Already have an account? <Link to="/login" style={{ fontWeight: 700 }}>Login →</Link>
        </div>
      </div>
    </div>
  );
}
