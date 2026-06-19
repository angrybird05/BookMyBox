import { useState } from "react";
import { Link } from "@tanstack/react-router";
import { useAuth } from "../context/AuthContext";

export default function Navbar() {
  const [open, setOpen] = useState(false);
  const { user, logout } = useAuth();
  return (
    <header className={`navbar ${open ? "open" : ""}`}>
      <div className="navbar-inner">
        <Link to="/" className="logo">BookMyBox</Link>
        <nav>
          <Link to="/">Home</Link>
          <Link to="/grounds">Grounds</Link>
          <Link to="/grounds">Pricing</Link>
          <Link to="/">About</Link>
        </nav>
        <div className="actions">
          {user ? (
            <>
              <Link to="/dashboard" className="neo-btn outline sm">Dashboard</Link>
              {user.role === "admin" && <Link to="/admin" className="neo-btn dark sm">Admin</Link>}
              <button className="neo-btn danger sm" onClick={logout}>Logout</button>
            </>
          ) : (
            <>
              <Link to="/login" className="neo-btn outline sm">Login</Link>
              <Link to="/grounds" className="neo-btn sm">Book Now</Link>
            </>
          )}
        </div>
        <button className="neo-btn sm hamburger" onClick={() => setOpen(o => !o)}>☰</button>
      </div>
    </header>
  );
}
