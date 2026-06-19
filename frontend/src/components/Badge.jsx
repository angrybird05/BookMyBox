export default function Badge({ variant = "", children }) {
  return <span className={`neo-badge ${variant}`}>{children}</span>;
}
