export default function SlotPicker({ slots, selectedIds, onToggle }) {
  return (
    <div className="slot-grid">
      {slots.map(s => {
        const selected = selectedIds.includes(s.id);
        const cls = ["slot", s.status === "booked" ? "booked" : "", selected ? "selected" : ""].join(" ");
        return (
          <button
            key={s.id}
            className={cls}
            disabled={s.status === "booked"}
            onClick={() => s.status !== "booked" && onToggle(s)}
          >
            <span className="t">{s.startTime} – {s.endTime} {selected ? "✓" : ""}</span>
            <span className="p">₹{s.price} • 1 hr</span>
          </button>
        );
      })}
    </div>
  );
}
