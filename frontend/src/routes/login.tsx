import { useState, useEffect, type FormEvent } from "react";
import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useAuth } from "../context/AuthContext";
import { z } from "zod";

const loginSearchSchema = z.object({
  role: z.enum(["user", "admin"]).optional(),
});

export const Route = createFileRoute("/login")({
  validateSearch: (search) => loginSearchSchema.parse(search),
  component: Login,
});

function Login() {
  const { login, pushToast } = useAuth();
  const navigate = useNavigate();
  const search = Route.useSearch();
  const initialRole = search.role || "user";

  const [role, setRole] = useState<"user" | "admin">(initialRole);
  const [email, setEmail] = useState(
    initialRole === "user" ? "user@bookmybox.com" : "admin@bookmybox.com"
  );
  const [password, setPassword] = useState(
    initialRole === "user" ? "password123" : "admin123"
  );
  const [error, setError] = useState("");
  const [isEmailFocused, setIsEmailFocused] = useState(false);
  const [isPasswordFocused, setIsPasswordFocused] = useState(false);

  const handleRoleChange = (newRole: "user" | "admin") => {
    setRole(newRole);
    setError("");
    if (newRole === "user") {
      setEmail("user@bookmybox.com");
      setPassword("password123");
    } else {
      setEmail("admin@bookmybox.com");
      setPassword("admin123");
    }
  };

  useEffect(() => {
    if (search.role && search.role !== role) {
      handleRoleChange(search.role);
    }
  }, [search.role]);

  const submit = async (e: FormEvent) => {
    e.preventDefault();
    if (!email || !password) { setError("Email and password are required"); return; }
    const res = await login(email, password);
    if (!res.ok) { setError(res.error || "Login failed"); return; }
    pushToast(`Welcome back, ${res.user!.name}!`, "success");
    navigate({ to: res.user!.role === "admin" ? "/admin" : "/dashboard" });
  };

  const instantLogin = async (demoEmail: string, demoPass: string) => {
    setError("");
    setEmail(demoEmail);
    setPassword(demoPass);
    const res = await login(demoEmail, demoPass);
    if (!res.ok) { setError(res.error || "Login failed"); return; }
    pushToast(`Welcome back, ${res.user!.name}!`, "success");
    navigate({ to: res.user!.role === "admin" ? "/admin" : "/dashboard" });
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
          <h1 style={{ fontSize: 24, margin: 0 }}>Welcome Back</h1>
          <span className="neo-badge dark" style={{
            background: role === "user" ? "var(--yellow)" : "var(--purple)",
            color: "var(--ink)",
            transition: "all 0.25s ease"
          }}>
            {role === "user" ? "🏏 PLAYER" : "👑 PARTNER"}
          </span>
        </div>

        <p style={{ fontSize: 13, marginBottom: 20, color: "#555" }}>
          {role === "user"
            ? "Reserve your slot in 60s, pay online and play with your squad."
            : "Manage your box cricket grounds, configure slots, and view reservations."}
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
            🏏 Player Flow
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
            👑 Partner Flow
          </button>
        </div>

        <form onSubmit={submit}>
          <div className="field">
            <label className="neo-label">Email Address</label>
            <input
              className="neo-input"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              onFocus={() => setIsEmailFocused(true)}
              onBlur={() => setIsEmailFocused(false)}
              style={{
                boxShadow: isEmailFocused ? `4px 4px 0 ${role === "user" ? "var(--yellow)" : "var(--purple)"}` : "none",
                transition: "all 0.1s ease"
              }}
            />
          </div>
          <div className="field">
            <label className="neo-label">Password</label>
            <input
              className="neo-input"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              onFocus={() => setIsPasswordFocused(true)}
              onBlur={() => setIsPasswordFocused(false)}
              style={{
                boxShadow: isPasswordFocused ? `4px 4px 0 ${role === "user" ? "var(--yellow)" : "var(--purple)"}` : "none",
                transition: "all 0.1s ease"
              }}
            />
          </div>

          {error && <div className="neo-error mb-4">{error}</div>}

          <button
            className="neo-btn block lg"
            type="submit"
            style={{
              background: role === "user" ? "var(--yellow)" : "var(--purple)",
              transition: "background 0.2s ease"
            }}
          >
            Login as {role === "user" ? "Player" : "Partner"} →
          </button>
        </form>

        <div className="flex between mt-4" style={{ fontSize: 13 }}>
          <a href="#" style={{ textDecoration: "underline" }}>Forgot password?</a>
          <Link to="/register" style={{ fontWeight: 700, textDecoration: "underline" }}>Register Account →</Link>
        </div>

        {/* Demo Quick Access Console */}
        <div style={{ marginTop: 24, padding: 16, background: "var(--light)", border: "2px solid var(--ink)", boxShadow: "var(--shadow-sm)" }}>
          <div style={{ fontSize: 11, fontFamily: "var(--mono)", fontWeight: 700, textTransform: "uppercase", marginBottom: 12, borderBottom: "2px dashed var(--ink)", paddingBottom: 6 }}>
            🛠️ Demo Quick Access Console
          </div>
          <div style={{ display: "grid", gap: "8px" }}>
            <button
              type="button"
              className="neo-btn outline sm"
              style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%" }}
              onClick={() => instantLogin("user@bookmybox.com", "password123")}
            >
              <span>🏏 Player Demo</span>
              <span className="neo-badge teal" style={{ padding: "2px 6px", fontSize: 9 }}>Log In Now</span>
            </button>
            <button
              type="button"
              className="neo-btn outline sm"
              style={{ display: "flex", justifyContent: "space-between", alignItems: "center", width: "100%" }}
              onClick={() => instantLogin("admin@bookmybox.com", "admin123")}
            >
              <span>👑 Admin Demo</span>
              <span className="neo-badge purple" style={{ padding: "2px 6px", fontSize: 9 }}>Log In Now</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
