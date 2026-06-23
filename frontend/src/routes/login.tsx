import { useState, type FormEvent } from "react";
import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useAuth } from "../context/AuthContext";

export const Route = createFileRoute("/login")({ component: Login });

function Login() {
  const { login, pushToast } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("user@bookmybox.com");
  const [password, setPassword] = useState("password123");
  const [error, setError] = useState("");

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (!email || !password) { setError("Email and password are required"); return; }
    const res = await login(email, password);
    if (!res.ok) { setError(res.error || "Login failed"); return; }
    pushToast(`Welcome back, ${res.user!.name}!`, "success");
    navigate({ to: res.user!.role === "admin" ? "/admin" : "/dashboard" });
  };


  return (
    <div className="auth-wrap">
      <div className="auth-card">
        <h1>Welcome Back</h1>
        <form onSubmit={submit}>
          <div className="field">
            <label className="neo-label">Email</label>
            <input className="neo-input" type="email" value={email} onChange={e => setEmail(e.target.value)} />
          </div>
          <div className="field">
            <label className="neo-label">Password</label>
            <input className="neo-input" type="password" value={password} onChange={e => setPassword(e.target.value)} />
          </div>
          {error && <div className="neo-error mb-4">{error}</div>}
          <button className="neo-btn block lg" type="submit">Login →</button>
        </form>
        <div className="flex between mt-4" style={{ fontSize: 13 }}>
          <a href="#">Forgot password?</a>
          <Link to="/register" style={{ fontWeight: 700 }}>Register →</Link>
        </div>
        <div className="divider">or</div>
        <button className="neo-btn outline block">G — Continue with Google</button>
        <div className="mt-4" style={{ fontSize: 12, padding: 10, background: "var(--light)", border: "2px solid var(--ink)" }}>
          <b>DEMO:</b> user@bookmybox.com / password123 — admin@bookmybox.com / admin123
        </div>
      </div>
    </div>
  );
}
