export default function Button({ variant = "primary", size, block, children, className = "", ...rest }) {
  const cls = ["neo-btn", variant, size, block ? "block" : "", className].filter(Boolean).join(" ");
  return <button className={cls} {...rest}>{children}</button>;
}
