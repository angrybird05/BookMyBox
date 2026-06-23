import { createContext, useContext, useEffect, useState } from "react";
import { apiLogin, apiRegister, apiVerifyOtp, apiLogout, apiGetMe, clearAuthData } from "../lib/api";

/** @type {React.Context<any>} */
const AuthContext = createContext(null);
const STORAGE_KEY = "bmb_user";

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [toasts, setToasts] = useState([]);

  useEffect(() => {
    try {
      const raw = typeof window !== "undefined" ? localStorage.getItem(STORAGE_KEY) : null;
      if (raw) {
        setUser(JSON.parse(raw));
      }
    } catch {}

    // Refresh profile state on boot
    const refreshProfile = async () => {
      try {
        const u = await apiGetMe();
        setUser(u);
        localStorage.setItem(STORAGE_KEY, JSON.stringify(u));
      } catch {
        // If unauthorized/expired, clear auth data
        clearAuthData();
        setUser(null);
      }
    };
    refreshProfile();
  }, []);

  const login = async (email, password) => {
    try {
      const data = await apiLogin({ email, password });
      setUser(data.user);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data.user));
      return { ok: true, user: data.user };
    } catch (err) {
      return { ok: false, error: err.message || "Invalid email or password" };
    }
  };

  const register = async (data) => {
    try {
      await apiRegister(data);
      return { ok: true };
    } catch (err) {
      return { ok: false, error: err.message || "Registration failed" };
    }
  };

  const verifyOtp = async (email, code) => {
    try {
      const data = await apiVerifyOtp(email, code);
      setUser(data.user);
      localStorage.setItem(STORAGE_KEY, JSON.stringify(data.user));
      return { ok: true, user: data.user };
    } catch (err) {
      return { ok: false, error: err.message || "Invalid OTP verification code" };
    }
  };

  const logout = async () => {
    try {
      await apiLogout();
    } catch {}
    clearAuthData();
    setUser(null);
    localStorage.removeItem(STORAGE_KEY);
  };

  const pushToast = (message, type = "info") => {
    const id = Date.now() + Math.random();
    setToasts(t => [...t, { id, message, type }]);
    setTimeout(() => setToasts(t => t.filter(x => x.id !== id)), 3000);
  };

  return (
    <AuthContext.Provider value={{ user, isAdmin: user?.role === "admin", login, logout, register, verifyOtp, toasts, pushToast }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}

