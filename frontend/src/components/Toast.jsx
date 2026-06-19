import { useAuth } from "../context/AuthContext";

export default function Toasts() {
  const { toasts } = useAuth();
  return (
    <div className="toasts">
      {toasts.map(t => (
        <div key={t.id} className={`toast ${t.type}`}>{t.message}</div>
      ))}
    </div>
  );
}
