export default function Modal({ open, onClose, children, title }) {
  if (!open) return null;
  return (
    <div className="modal-backdrop" onClick={onClose}>
      <div className="modal" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose}>✕</button>
        {title && <h2 style={{ textTransform: "uppercase", fontWeight: 800, marginBottom: 16 }}>{title}</h2>}
        {children}
      </div>
    </div>
  );
}
