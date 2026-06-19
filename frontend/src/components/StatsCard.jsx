/**
 * @param {{ value: any, label: any, bg?: string, icon?: any }} props
 */
export default function StatsCard({ value, label, bg = "var(--yellow)", icon }) {
  return (
    <div className="stat-card" style={{ background: bg }}>
      {icon && <div style={{ fontSize: 24 }}>{icon}</div>}
      <span className="num">{value}</span>
      <span className="lbl">{label}</span>
    </div>
  );
}
