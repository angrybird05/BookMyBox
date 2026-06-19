import { Link } from "@tanstack/react-router";
import Badge from "./Badge";

const tagVariant = (t) => t === "PREMIUM" ? "purple" : t === "NEW" ? "green" : "coral";

export default function GroundCard({ g }) {
  const lowSlots = g.availableSlots <= 5;
  return (
    <Link to="/grounds/$id" params={{ id: g.id }} className="ground-card">
      <div className="img" style={{ background: g.gradient }}>
        {g.tag && <span className="tag"><Badge variant={tagVariant(g.tag)}>{g.tag}</Badge></span>}
        <span>{g.icon}</span>
      </div>
      <div className="body">
        <h3>{g.name}</h3>
        <div className="loc">📍 {g.location}, {g.city}</div>
        <div className="amen">
          {g.amenities.slice(0, 3).map(a => <Badge key={a} variant="white">{a}</Badge>)}
        </div>
        <div className="meta">
          <span>★ {g.rating} ({g.reviewCount})</span>
          <Badge variant={lowSlots ? "coral" : "green"}>{g.availableSlots} slots left</Badge>
        </div>
        <div className="meta">
          <span className="price">₹{g.price}<span style={{ fontSize: 12 }}>/hr</span></span>
        </div>
        <button className="neo-btn block">Book Now →</button>
      </div>
    </Link>
  );
}
