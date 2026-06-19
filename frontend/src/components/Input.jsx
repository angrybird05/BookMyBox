export default function Input({ label, error, id, ...rest }) {
  const inputId = id || rest.name || Math.random().toString(36).slice(2);
  return (
    <div className="field">
      {label && <label className="neo-label" htmlFor={inputId}>{label}</label>}
      <input id={inputId} className="neo-input" {...rest} />
      {error && <div className="neo-error">{error}</div>}
    </div>
  );
}
