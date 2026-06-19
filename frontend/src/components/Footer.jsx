import { Link } from "@tanstack/react-router";
export default function Footer() {
  return (
    <footer className="footer">
      <div className="container">
        <div className="footer-grid">
          <div>
            <div className="logo mono" style={{ fontSize: 24, color: "var(--yellow)", fontWeight: 700 }}>BookMyBox</div>
            <p style={{ marginTop: 8, color: "#bbb" }}>Book box cricket grounds in 60 seconds. No hidden fees. Just play.</p>
          </div>
          <div>
            <h4>Explore</h4>
            <ul>
              <li><Link to="/grounds">Grounds</Link></li>
              <li><Link to="/">Pricing</Link></li>
              <li><Link to="/">About</Link></li>
            </ul>
          </div>
          <div>
            <h4>Help</h4>
            <ul>
              <li><Link to="/">Contact</Link></li>
              <li><Link to="/">Privacy</Link></li>
              <li><Link to="/">Terms</Link></li>
            </ul>
          </div>
          <div>
            <h4>Follow</h4>
            <div style={{ display: "flex", gap: 10, fontSize: 20 }}>
              <span>𝕏</span><span>📷</span><span>▶️</span><span>📘</span>
            </div>
          </div>
        </div>
        <div className="footer-bottom">© 2026 BookMyBox. All rights reserved.</div>
      </div>
    </footer>
  );
}
