import { createContext, useContext, useEffect, useState } from "react";
import { users as mockUsers } from "../data/mockData";

/** @type {React.Context<any>} */
const AuthContext = createContext(null);
const STORAGE_KEY = "bmb_user";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    try {
      const raw = typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
      if (raw) setUser(JSON.parse(raw));
    } catch {}
  }, []);

  const login = (email, password) => {
    const found = mockUsers.find(u => u.email.toLowerCase() === email.toLowerCase() && u.password === password);
    if (!found) return { ok: false, error: "Invalid email or password" };
    const { password: _p, ...safe } = found;
    setUser(safe);
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(safe)); } catch {}
    return { ok: true, user: safe };
  };

  const register = (data) => {
    const existing = mockUsers.find(u => u.email.toLowerCase() === data.email.toLowerCase());
    if (existing) return { ok: false, error: "Email already registered" };
    const role = data.role || "user";
    const newUser = { id: `u${Date.now()}`, ...data, role, wallet: 0, totalSpent: 0, bookings: 0, status: "ACTIVE" };
    mockUsers.push({ ...newUser, password: data.password });
    const { password: _p, ...safe } = newUser;
    setUser(safe);
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(safe)); } catch {}
    return { ok: true, user: safe };
  };

  const logout = () => {
    setUser(null);
    try { localStorage.removeItem(STORAGE_KEY); } catch {}
  };

  const pushToast = (message, type = "info") => {
    const id = Date.now() + Math.random();
    setToasts(t => [...t, { id, message, type }]);
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 3000);
  };

  return (
    <AuthContext.Provider value={{ user, isAdmin: user?.role === "admin", login, logout, register, toasts, pushToast }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}
