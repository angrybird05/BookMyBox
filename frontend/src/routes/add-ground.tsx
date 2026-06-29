import { useState, type FormEvent } from "react";
import { createFileRoute, useNavigate, Link } from "@tanstack/react-router";
import { useAuth } from "../context/AuthContext";

export const Route = createFileRoute("/add-ground")({ component: AddGround });

const AMENITY_OPTIONS = [
  { id: "floodlights", label: "Floodlights", icon: "💡" },
  { id: "parking", label: "Parking", icon: "🚗" },
  { id: "changing_room", label: "Changing Room", icon: "🚿" },
  { id: "cafeteria", label: "Cafeteria / Canteen", icon: "🍔" },
  { id: "live_scoring", label: "Live Scoring", icon: "📊" },
  { id: "live_streaming", label: "Live Streaming", icon: "🎥" },
  { id: "coaching", label: "Coaching Area", icon: "🏋️" },
  { id: "first_aid", label: "First Aid", icon: "🩺" },
  { id: "restrooms", label: "Restrooms", icon: "🚻" },
  { id: "wifi", label: "Wi-Fi", icon: "📶" },
];

const OFFER_TEMPLATES = [
  "10% off on 3+ slot bookings",
  "Free slot on 5th booking",
  "Weekend discount 15%",
  "Corporate group discount 20%",
];

interface FormState {
  name: string;
  address: string;
  location: string;
  city: string;
  pincode: string;
  mapLink: string;
  ownerName: string;
  contactPhone: string;
  contactEmail: string;
  whatsapp: string;
  pricePerHour: string;
  depositAmount: string;
  openTime: string;
  closeTime: string;
  slotDuration: string;
  description: string;
  totalBoxes: string;
  surfaceType: string;
  offers: string;
  customOffer: string;
  amenities: string[];
  images: string;
}

const INIT: FormState = {
  name: "",
  address: "",
  location: "",
  city: "",
  pincode: "",
  mapLink: "",
  ownerName: "",
  contactPhone: "",
  contactEmail: "",
  whatsapp: "",
  pricePerHour: "",
  depositAmount: "",
  openTime: "06:00",
  closeTime: "23:00",
  slotDuration: "60",
  description: "",
  totalBoxes: "1",
  surfaceType: "astro-turf",
  offers: "",
  customOffer: "",
  amenities: [],
  images: "",
};

function StepBadge({ n, active, done }: { n: number; active: boolean; done: boolean }) {
  return (
    <div
      style={{
        width: 40,
        height: 40,
        borderRadius: "50%",
        border: "3px solid var(--ink)",
        background: done ? "var(--teal)" : active ? "var(--yellow)" : "var(--white)",
        display: "flex",
        alignItems: "center",
        justifyContent: "center",
        fontWeight: 800,
        fontFamily: "var(--mono)",
        fontSize: 16,
        boxShadow: active ? "var(--shadow)" : "var(--shadow-sm)",
        transition: "all 0.2s ease",
        flexShrink: 0,
      }}
    >
      {done ? "✓" : n}
    </div>
  );
}

function AddGround() {
  const { user, pushToast } = useAuth();
  const navigate = useNavigate();
  const [step, setStep] = useState(1);
  const [form, setForm] = useState<FormState>(INIT);
  const [errors, setErrors] = useState<Partial<FormState>>({});
  const [submitted, setSubmitted] = useState(false);

  const totalSteps = 4;

  const set = (field: keyof FormState, value: string | string[]) =>
    setForm((f) => ({ ...f, [field]: value }));

  const toggleAmenity = (id: string) => {
    set(
      "amenities",
      form.amenities.includes(id)
        ? form.amenities.filter((a) => a !== id)
        : [...form.amenities, id]
    );
  };

  const validate = (s: number): boolean => {
    const e: Partial<FormState> = {};
    if (s === 1) {
      if (!form.name.trim()) e.name = "Ground name is required";
      if (!form.address.trim()) e.address = "Address is required";
      if (!form.location.trim()) e.location = "Locality / area is required";
      if (!form.city.trim()) e.city = "City is required";
    }
    if (s === 2) {
      if (!form.ownerName.trim()) e.ownerName = "Owner name is required";
      if (!form.contactPhone.trim()) e.contactPhone = "Phone number is required";
      if (!form.contactEmail.trim()) e.contactEmail = "Email is required";
    }
    if (s === 3) {
      if (!form.pricePerHour.trim()) e.pricePerHour = "Price per hour is required";
      if (!form.openTime) e.openTime = "Opening time is required" as any;
      if (!form.closeTime) e.closeTime = "Closing time is required" as any;
    }
    setErrors(e);
    return Object.keys(e).length === 0;
  };

  const nextStep = () => {
    if (validate(step)) setStep((s) => Math.min(s + 1, totalSteps));
  };
  const prevStep = () => setStep((s) => Math.max(s - 1, 1));

  const handleSubmit = (e: FormEvent) => {
    e.preventDefault();
    if (!validate(step)) return;
    setSubmitted(true);
    pushToast("🎉 Ground submitted for review! We'll contact you shortly.", "success");
    setTimeout(() => navigate({ to: "/" }), 3000);
  };

  const stepLabels = ["Ground Info", "Contact", "Pricing & Timings", "Offers & Extras"];

  if (submitted) {
    return (
      <div style={{ minHeight: "80vh", display: "flex", alignItems: "center", justifyContent: "center", padding: "40px 24px" }}>
        <div className="neo-card text-center" style={{ maxWidth: 520, width: "100%" }}>
          <div style={{ fontSize: 72, marginBottom: 16 }}>🏏</div>
          <h1 style={{ fontSize: 32, fontWeight: 800, textTransform: "uppercase", marginBottom: 12 }}>
            Ground Submitted!
          </h1>
          <p style={{ fontSize: 16, marginBottom: 24, color: "#555" }}>
            <b>{form.name}</b> has been submitted for review. Our team will verify the details and get back to you at <b>{form.contactEmail}</b> within 24 hours.
          </p>
          <div style={{ background: "var(--yellow)", border: "var(--border)", padding: "12px 20px", marginBottom: 24, fontWeight: 700 }}>
            📞 You'll receive a call at {form.contactPhone}
          </div>
          <Link to="/" className="neo-btn lg block">Back to Home →</Link>
        </div>
      </div>
    );
  }

  return (
    <>
      {/* Hero banner */}
      <section style={{ background: "var(--ink)", color: "var(--white)", borderBottom: "var(--border)", padding: "40px 0" }}>
        <div className="container">
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", flexWrap: "wrap", gap: 16 }}>
            <div>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 8 }}>
                <span style={{ background: "var(--yellow)", color: "var(--ink)", padding: "4px 12px", fontWeight: 800, border: "var(--border)", fontSize: 12, textTransform: "uppercase", letterSpacing: "0.05em" }}>Ground Owner Portal</span>
              </div>
              <h1 style={{ fontSize: 48, fontWeight: 800, textTransform: "uppercase", letterSpacing: "-0.03em", lineHeight: 1 }}>
                List Your<br />
                <span style={{ color: "var(--yellow)", WebkitTextStroke: "2px var(--yellow)" }}>Cricket Ground</span>
              </h1>
              <p style={{ marginTop: 12, fontSize: 16, color: "#ccc", maxWidth: 480 }}>
                Join 50+ ground owners on BookMyBox. Reach thousands of players, manage bookings effortlessly, and grow your revenue.
              </p>
            </div>
            <div style={{ display: "grid", gap: 12 }}>
              {[
                { icon: "📈", text: "10,000+ active players" },
                { icon: "💰", text: "Instant payment settlements" },
                { icon: "📱", text: "Smart booking management" },
              ].map((item) => (
                <div key={item.text} style={{ background: "var(--white)", color: "var(--ink)", border: "var(--border)", padding: "10px 16px", fontWeight: 700, display: "flex", gap: 10, alignItems: "center", boxShadow: "var(--shadow-sm)" }}>
                  <span style={{ fontSize: 20 }}>{item.icon}</span>
                  {item.text}
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Step progress indicator */}
      <section style={{ background: "var(--light)", borderBottom: "var(--border)", padding: "0" }}>
        <div className="container" style={{ padding: "0 24px" }}>
          <div style={{ display: "flex", alignItems: "stretch", overflowX: "auto" }}>
            {stepLabels.map((label, i) => {
              const n = i + 1;
              const isActive = step === n;
              const isDone = step > n;
              return (
                <div
                  key={n}
                  onClick={() => isDone && setStep(n)}
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 12,
                    padding: "16px 24px",
                    borderRight: "var(--border)",
                    background: isActive ? "var(--yellow)" : isDone ? "var(--teal)" : "transparent",
                    cursor: isDone ? "pointer" : "default",
                    transition: "all 0.15s ease",
                    flexShrink: 0,
                    minWidth: 160,
                  }}
                >
                  <StepBadge n={n} active={isActive} done={isDone} />
                  <div>
                    <div style={{ fontSize: 11, textTransform: "uppercase", letterSpacing: "0.05em", fontWeight: 700, opacity: 0.7 }}>Step {n}</div>
                    <div style={{ fontWeight: 800, fontSize: 14, textTransform: "uppercase" }}>{label}</div>
                  </div>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Main form */}
      <section className="container" style={{ padding: "48px 24px" }}>
        <form onSubmit={handleSubmit}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 340px", gap: 32, alignItems: "start" }}>

            {/* Left - form fields */}
            <div>
              {/* ── STEP 1: Ground Info ── */}
              {step === 1 && (
                <div>
                  <h2 className="section-title">Ground Information</h2>

                  <div className="field">
                    <label className="neo-label">Ground / Venue Name *</label>
                    <input
                      id="ground-name"
                      className="neo-input"
                      placeholder="e.g. Sixer Arena, PowerPlay Box..."
                      value={form.name}
                      onChange={(e) => set("name", e.target.value)}
                    />
                    {errors.name && <div className="neo-error">{errors.name}</div>}
                  </div>

                  <div className="field">
                    <label className="neo-label">Full Address *</label>
                    <textarea
                      id="ground-address"
                      className="neo-input"
                      rows={3}
                      placeholder="Door No., Street, Landmark..."
                      value={form.address}
                      onChange={(e) => set("address", e.target.value)}
                    />
                    {errors.address && <div className="neo-error">{errors.address}</div>}
                  </div>

                  <div className="form-row">
                    <div className="field">
                      <label className="neo-label">Locality / Area *</label>
                      <input
                        id="ground-location"
                        className="neo-input"
                        placeholder="e.g. Hitech City, Gachibowli"
                        value={form.location}
                        onChange={(e) => set("location", e.target.value)}
                      />
                      {errors.location && <div className="neo-error">{errors.location}</div>}
                    </div>
                    <div className="field">
                      <label className="neo-label">City *</label>
                      <input
                        id="ground-city"
                        className="neo-input"
                        placeholder="e.g. Hyderabad"
                        value={form.city}
                        onChange={(e) => set("city", e.target.value)}
                      />
                      {errors.city && <div className="neo-error">{errors.city}</div>}
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="field">
                      <label className="neo-label">PIN Code</label>
                      <input
                        id="ground-pincode"
                        className="neo-input"
                        placeholder="500032"
                        maxLength={6}
                        value={form.pincode}
                        onChange={(e) => set("pincode", e.target.value)}
                      />
                    </div>
                    <div className="field">
                      <label className="neo-label">Number of Boxes / Courts</label>
                      <select
                        id="ground-total-boxes"
                        className="neo-input"
                        value={form.totalBoxes}
                        onChange={(e) => set("totalBoxes", e.target.value)}
                      >
                        {[1,2,3,4,5,6,8,10].map((n) => (
                          <option key={n} value={n}>{n} Box{n > 1 ? "es" : ""}</option>
                        ))}
                      </select>
                    </div>
                  </div>

                  <div className="field">
                    <label className="neo-label">Google Maps Link</label>
                    <input
                      id="ground-map-link"
                      className="neo-input"
                      placeholder="https://maps.google.com/..."
                      value={form.mapLink}
                      onChange={(e) => set("mapLink", e.target.value)}
                    />
                    <div style={{ fontSize: 12, marginTop: 6, color: "#666" }}>Paste your Google Maps share link so players can easily find you</div>
                  </div>

                  <div className="field">
                    <label className="neo-label">Surface Type</label>
                    <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 4 }}>
                      {["astro-turf", "synthetic", "concrete", "natural-grass"].map((s) => (
                        <label
                          key={s}
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: 8,
                            padding: "10px 16px",
                            border: "var(--border)",
                            background: form.surfaceType === s ? "var(--yellow)" : "var(--white)",
                            cursor: "pointer",
                            fontWeight: 700,
                            fontSize: 13,
                            textTransform: "uppercase",
                            boxShadow: form.surfaceType === s ? "var(--shadow)" : "var(--shadow-sm)",
                            transition: "all 0.1s ease",
                          }}
                        >
                          <input
                            type="radio"
                            name="surfaceType"
                            value={s}
                            checked={form.surfaceType === s}
                            onChange={() => set("surfaceType", s)}
                            style={{ display: "none" }}
                          />
                          {s.replace("-", " ")}
                        </label>
                      ))}
                    </div>
                  </div>

                  <div className="field">
                    <label className="neo-label">Ground Description</label>
                    <textarea
                      id="ground-description"
                      className="neo-input"
                      rows={4}
                      placeholder="Describe your ground — turf quality, seating, special features, what makes it unique..."
                      value={form.description}
                      onChange={(e) => set("description", e.target.value)}
                    />
                    <div style={{ fontSize: 12, marginTop: 6, color: "#666" }}>{form.description.length}/500 characters</div>
                  </div>
                </div>
              )}

              {/* ── STEP 2: Contact Details ── */}
              {step === 2 && (
                <div>
                  <h2 className="section-title">Contact Details</h2>

                  <div className="field">
                    <label className="neo-label">Owner / Manager Name *</label>
                    <input
                      id="owner-name"
                      className="neo-input"
                      placeholder="Full name"
                      value={form.ownerName}
                      onChange={(e) => set("ownerName", e.target.value)}
                    />
                    {errors.ownerName && <div className="neo-error">{errors.ownerName}</div>}
                  </div>

                  <div className="form-row">
                    <div className="field">
                      <label className="neo-label">Phone Number *</label>
                      <input
                        id="contact-phone"
                        className="neo-input"
                        type="tel"
                        placeholder="+91 98765 43210"
                        value={form.contactPhone}
                        onChange={(e) => set("contactPhone", e.target.value)}
                      />
                      {errors.contactPhone && <div className="neo-error">{errors.contactPhone}</div>}
                    </div>
                    <div className="field">
                      <label className="neo-label">WhatsApp Number</label>
                      <input
                        id="whatsapp-number"
                        className="neo-input"
                        type="tel"
                        placeholder="+91 98765 43210"
                        value={form.whatsapp}
                        onChange={(e) => set("whatsapp", e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="field">
                    <label className="neo-label">Email Address *</label>
                    <input
                      id="contact-email"
                      className="neo-input"
                      type="email"
                      placeholder="yourground@email.com"
                      value={form.contactEmail}
                      onChange={(e) => set("contactEmail", e.target.value)}
                    />
                    {errors.contactEmail && <div className="neo-error">{errors.contactEmail}</div>}
                  </div>

                  <div style={{ background: "var(--light)", border: "var(--border)", padding: 20, marginTop: 8 }}>
                    <div style={{ fontWeight: 800, textTransform: "uppercase", marginBottom: 8 }}>📞 Contact Visibility</div>
                    <p style={{ fontSize: 14, color: "#555", marginBottom: 16 }}>Choose what contact info players can see on your listing:</p>
                    {[
                      { id: "show_phone", label: "Show phone number publicly" },
                      { id: "show_whatsapp", label: "Enable WhatsApp booking requests" },
                      { id: "show_email", label: "Show email address publicly" },
                    ].map((opt) => (
                      <label key={opt.id} style={{ display: "flex", gap: 10, alignItems: "center", marginBottom: 10, cursor: "pointer", fontWeight: 600, fontSize: 14 }}>
                        <input type="checkbox" defaultChecked id={opt.id} style={{ width: 18, height: 18, accentColor: "var(--ink)" }} />
                        {opt.label}
                      </label>
                    ))}
                  </div>

                  {!user && (
                    <div style={{ background: "var(--coral)", color: "var(--white)", border: "var(--border)", padding: 16, marginTop: 20, fontWeight: 700 }}>
                      ⚠️ You're not logged in. <Link to="/login" search={{ role: "admin" }} style={{ color: "var(--yellow)" }}>Login or Register</Link> to save your ground listing to your account.
                    </div>
                  )}
                </div>
              )}

              {/* ── STEP 3: Pricing & Timings ── */}
              {step === 3 && (
                <div>
                  <h2 className="section-title">Pricing & Timings</h2>

                  <div style={{ background: "var(--yellow)", border: "var(--border)", padding: 16, marginBottom: 24, boxShadow: "var(--shadow)" }}>
                    <div style={{ fontWeight: 800, textTransform: "uppercase", fontSize: 13 }}>💡 Pricing Tip</div>
                    <div style={{ fontSize: 13, marginTop: 4 }}>Average box cricket price in Hyderabad is ₹700–₹1,000/hr. Competitive pricing boosts your bookings by up to 40%.</div>
                  </div>

                  <div className="form-row">
                    <div className="field">
                      <label className="neo-label">Price per Hour (₹) *</label>
                      <input
                        id="price-per-hour"
                        className="neo-input"
                        type="number"
                        min="100"
                        max="5000"
                        step="50"
                        placeholder="800"
                        value={form.pricePerHour}
                        onChange={(e) => set("pricePerHour", e.target.value)}
                      />
                      {errors.pricePerHour && <div className="neo-error">{errors.pricePerHour}</div>}
                    </div>
                    <div className="field">
                      <label className="neo-label">Advance Deposit (₹)</label>
                      <input
                        id="deposit-amount"
                        className="neo-input"
                        type="number"
                        min="0"
                        step="50"
                        placeholder="0 (no deposit)"
                        value={form.depositAmount}
                        onChange={(e) => set("depositAmount", e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="form-row">
                    <div className="field">
                      <label className="neo-label">Opening Time *</label>
                      <input
                        id="open-time"
                        className="neo-input"
                        type="time"
                        value={form.openTime}
                        onChange={(e) => set("openTime", e.target.value)}
                      />
                    </div>
                    <div className="field">
                      <label className="neo-label">Closing Time *</label>
                      <input
                        id="close-time"
                        className="neo-input"
                        type="time"
                        value={form.closeTime}
                        onChange={(e) => set("closeTime", e.target.value)}
                      />
                    </div>
                  </div>

                  <div className="field">
                    <label className="neo-label">Slot Duration</label>
                    <div style={{ display: "flex", gap: 10, flexWrap: "wrap", marginTop: 4 }}>
                      {[
                        { value: "30", label: "30 min" },
                        { value: "60", label: "1 hour" },
                        { value: "90", label: "1.5 hrs" },
                        { value: "120", label: "2 hours" },
                      ].map((opt) => (
                        <label
                          key={opt.value}
                          style={{
                            display: "flex",
                            alignItems: "center",
                            gap: 8,
                            padding: "12px 20px",
                            border: "var(--border)",
                            background: form.slotDuration === opt.value ? "var(--teal)" : "var(--white)",
                            cursor: "pointer",
                            fontWeight: 800,
                            fontFamily: "var(--mono)",
                            fontSize: 14,
                            boxShadow: form.slotDuration === opt.value ? "var(--shadow)" : "var(--shadow-sm)",
                            transition: "all 0.1s ease",
                          }}
                        >
                          <input
                            type="radio"
                            name="slotDuration"
                            value={opt.value}
                            checked={form.slotDuration === opt.value}
                            onChange={() => set("slotDuration", opt.value)}
                            style={{ display: "none" }}
                          />
                          {opt.label}
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Weekly schedule */}
                  <div className="field" style={{ marginTop: 8 }}>
                    <label className="neo-label">Working Days</label>
                    <div style={{ display: "flex", gap: 8, flexWrap: "wrap", marginTop: 8 }}>
                      {["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].map((day) => (
                        <label
                          key={day}
                          style={{
                            padding: "10px 14px",
                            border: "var(--border)",
                            background: ["Sat","Sun"].includes(day) ? "var(--yellow)" : "var(--white)",
                            cursor: "pointer",
                            fontWeight: 800,
                            fontFamily: "var(--mono)",
                            fontSize: 13,
                            boxShadow: "var(--shadow-sm)",
                          }}
                        >
                          <input type="checkbox" defaultChecked style={{ marginRight: 6, accentColor: "var(--ink)" }} />
                          {day}
                        </label>
                      ))}
                    </div>
                  </div>

                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginTop: 20 }}>
                    {[
                      { label: "Peak Hours (6PM-10PM)", id: "peak" },
                      { label: "Weekend Pricing", id: "weekend" },
                    ].map((item) => (
                      <div key={item.id} style={{ border: "var(--border)", padding: 16, background: "var(--white)", boxShadow: "var(--shadow-sm)" }}>
                        <label style={{ display: "flex", gap: 10, alignItems: "center", cursor: "pointer", fontWeight: 700, marginBottom: 10 }}>
                          <input type="checkbox" id={item.id} style={{ width: 18, height: 18, accentColor: "var(--ink)" }} />
                          {item.label}
                        </label>
                        <input className="neo-input" type="number" placeholder="Extra ₹ per hour" style={{ fontSize: 13 }} />
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* ── STEP 4: Offers & Extras ── */}
              {step === 4 && (
                <div>
                  <h2 className="section-title">Offers & Extras</h2>

                  {/* Amenities */}
                  <div className="field">
                    <label className="neo-label">Amenities & Facilities</label>
                    <p style={{ fontSize: 13, color: "#555", marginBottom: 12 }}>Select all that are available at your ground:</p>
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(2, 1fr)", gap: 10 }}>
                      {AMENITY_OPTIONS.map((opt) => {
                        const checked = form.amenities.includes(opt.id);
                        return (
                          <label
                            key={opt.id}
                            htmlFor={`amenity-${opt.id}`}
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: 12,
                              padding: "12px 16px",
                              border: "var(--border)",
                              background: checked ? "var(--green)" : "var(--white)",
                              cursor: "pointer",
                              fontWeight: 700,
                              fontSize: 14,
                              boxShadow: checked ? "var(--shadow)" : "var(--shadow-sm)",
                              transition: "all 0.12s ease",
                              transform: checked ? "translate(-1px, -1px)" : "none",
                            }}
                          >
                            <input
                              type="checkbox"
                              id={`amenity-${opt.id}`}
                              checked={checked}
                              onChange={() => toggleAmenity(opt.id)}
                              style={{ display: "none" }}
                            />
                            <span style={{ fontSize: 20 }}>{opt.icon}</span>
                            {opt.label}
                            {checked && <span style={{ marginLeft: "auto", color: "var(--ink)" }}>✓</span>}
                          </label>
                        );
                      })}
                    </div>
                  </div>

                  {/* Offers */}
                  <div className="field" style={{ marginTop: 24 }}>
                    <label className="neo-label">Offers & Discounts</label>
                    <p style={{ fontSize: 13, color: "#555", marginBottom: 12 }}>Choose quick offer templates or write your own:</p>
                    <div style={{ display: "grid", gap: 8, marginBottom: 16 }}>
                      {OFFER_TEMPLATES.map((tmpl) => {
                        const active = form.offers.includes(tmpl);
                        return (
                          <label
                            key={tmpl}
                            style={{
                              display: "flex",
                              alignItems: "center",
                              gap: 12,
                              padding: "12px 16px",
                              border: "var(--border)",
                              background: active ? "var(--coral)" : "var(--white)",
                              color: active ? "var(--white)" : "var(--ink)",
                              cursor: "pointer",
                              fontWeight: 700,
                              fontSize: 14,
                              boxShadow: active ? "var(--shadow)" : "var(--shadow-sm)",
                              transition: "all 0.12s ease",
                            }}
                          >
                            <input
                              type="checkbox"
                              checked={active}
                              onChange={() => {
                                const curr = form.offers;
                                set("offers", active ? curr.replace(tmpl, "").trim() : (curr ? curr + "\n" + tmpl : tmpl));
                              }}
                              style={{ display: "none" }}
                            />
                            🏷️ {tmpl}
                            {active && <span style={{ marginLeft: "auto" }}>✓</span>}
                          </label>
                        );
                      })}
                    </div>
                    <label className="neo-label">Custom Offer / Terms</label>
                    <textarea
                      id="custom-offer"
                      className="neo-input"
                      rows={3}
                      placeholder="e.g. Birthday party package — book 4 hrs get 1 free, corporate tournament packages..."
                      value={form.customOffer}
                      onChange={(e) => set("customOffer", e.target.value)}
                    />
                  </div>

                  {/* Photo links */}
                  <div className="field" style={{ marginTop: 24 }}>
                    <label className="neo-label">Ground Photo Links (optional)</label>
                    <textarea
                      id="ground-images"
                      className="neo-input"
                      rows={3}
                      placeholder="Paste image URLs or Google Drive/Photos links, one per line..."
                      value={form.images}
                      onChange={(e) => set("images", e.target.value)}
                    />
                    <div style={{ fontSize: 12, marginTop: 6, color: "#666" }}>Our team will contact you to collect photos directly if needed</div>
                  </div>

                  {/* Extra notes */}
                  <div className="field" style={{ marginTop: 8 }}>
                    <label className="neo-label">Any Other Information</label>
                    <textarea
                      id="extra-notes"
                      className="neo-input"
                      rows={3}
                      placeholder="Tournament hosting capabilities, corporate packages, special rules, nearby landmarks..."
                    />
                  </div>

                  {/* Terms */}
                  <div style={{ border: "var(--border)", padding: 16, background: "var(--white)", marginTop: 16, boxShadow: "var(--shadow-sm)" }}>
                    <label style={{ display: "flex", gap: 12, alignItems: "flex-start", cursor: "pointer", fontWeight: 600, fontSize: 14 }}>
                      <input type="checkbox" required id="terms-agree" style={{ width: 18, height: 18, marginTop: 2, accentColor: "var(--ink)", flexShrink: 0 }} />
                      <span>
                        I confirm that the above information is accurate and I am authorized to list this ground on BookMyBox. I agree to the{" "}
                        <a href="#" style={{ fontWeight: 800, textDecoration: "underline" }}>Terms & Conditions</a>{" "}
                        and{" "}
                        <a href="#" style={{ fontWeight: 800, textDecoration: "underline" }}>Ground Owner Policy</a>.
                      </span>
                    </label>
                  </div>
                </div>
              )}

              {/* Navigation buttons */}
              <div style={{ display: "flex", gap: 12, marginTop: 32, flexWrap: "wrap" }}>
                {step > 1 && (
                  <button type="button" className="neo-btn outline" onClick={prevStep} id="btn-prev">
                    ← Back
                  </button>
                )}
                {step < totalSteps ? (
                  <button type="button" className="neo-btn lg" onClick={nextStep} id="btn-next" style={{ flex: 1 }}>
                    Continue to {stepLabels[step]} →
                  </button>
                ) : (
                  <button type="submit" className="neo-btn lg secondary" id="btn-submit" style={{ flex: 1 }}>
                    🚀 Submit Ground for Review
                  </button>
                )}
              </div>
            </div>

            {/* Right - summary card */}
            <div style={{ position: "sticky", top: 90 }}>
              {/* Ground preview */}
              <div className="neo-card" style={{ marginBottom: 20 }}>
                <div style={{ fontWeight: 800, textTransform: "uppercase", fontSize: 13, marginBottom: 16, borderBottom: "2px solid var(--ink)", paddingBottom: 8 }}>
                  📋 Your Listing Preview
                </div>
                <div style={{ background: form.name ? "linear-gradient(135deg,var(--yellow),var(--coral))" : "var(--light)", border: "var(--border)", height: 100, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 40, marginBottom: 12 }}>
                  🏏
                </div>
                <div style={{ fontWeight: 800, fontSize: 18, textTransform: "uppercase", marginBottom: 4 }}>
                  {form.name || <span style={{ color: "#aaa", fontWeight: 400, textTransform: "none", fontSize: 15 }}>Ground name will appear here</span>}
                </div>
                {form.location && (
                  <div style={{ fontSize: 13, color: "#555", marginBottom: 6 }}>📍 {form.location}{form.city ? `, ${form.city}` : ""}</div>
                )}
                {form.pricePerHour && (
                  <div className="mono" style={{ fontSize: 22, fontWeight: 700, marginBottom: 8 }}>₹{form.pricePerHour}/hr</div>
                )}
                {form.openTime && form.closeTime && (
                  <div style={{ fontSize: 13, color: "#555", marginBottom: 8 }}>⏰ {form.openTime} – {form.closeTime}</div>
                )}
                {form.amenities.length > 0 && (
                  <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 8 }}>
                    {form.amenities.slice(0, 4).map((id) => {
                      const a = AMENITY_OPTIONS.find((o) => o.id === id);
                      return a ? (
                        <span key={id} className="neo-badge teal" style={{ fontSize: 11 }}>{a.icon} {a.label}</span>
                      ) : null;
                    })}
                    {form.amenities.length > 4 && (
                      <span className="neo-badge" style={{ fontSize: 11 }}>+{form.amenities.length - 4} more</span>
                    )}
                  </div>
                )}
              </div>

              {/* Why list with us */}
              <div className="neo-card" style={{ background: "var(--ink)", color: "var(--white)" }}>
                <div style={{ fontWeight: 800, textTransform: "uppercase", fontSize: 13, color: "var(--yellow)", marginBottom: 16, borderBottom: "1px solid #333", paddingBottom: 8 }}>
                  🌟 Why BookMyBox?
                </div>
                {[
                  { icon: "₹0", text: "Zero listing fees" },
                  { icon: "📱", text: "Mobile booking app" },
                  { icon: "⚡", text: "Instant payment" },
                  { icon: "📊", text: "Analytics dashboard" },
                  { icon: "🔒", text: "Secure transactions" },
                  { icon: "🤝", text: "Dedicated support" },
                ].map((item) => (
                  <div key={item.text} style={{ display: "flex", gap: 12, alignItems: "center", marginBottom: 12, fontSize: 14 }}>
                    <span style={{ background: "var(--yellow)", color: "var(--ink)", width: 36, height: 36, display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontFamily: "var(--mono)", fontSize: 13, border: "2px solid var(--yellow)", flexShrink: 0 }}>{item.icon}</span>
                    {item.text}
                  </div>
                ))}
              </div>

              {/* Step counter */}
              <div style={{ marginTop: 16, border: "var(--border)", padding: "12px 16px", background: "var(--white)", boxShadow: "var(--shadow-sm)", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span style={{ fontWeight: 700, fontSize: 13, textTransform: "uppercase" }}>Progress</span>
                <span className="mono" style={{ fontWeight: 800 }}>{step}/{totalSteps}</span>
              </div>
              <div style={{ height: 8, background: "var(--light)", border: "var(--border)", borderTop: "none", marginTop: -1 }}>
                <div style={{ height: "100%", background: "var(--yellow)", width: `${(step / totalSteps) * 100}%`, transition: "width 0.3s ease", borderRight: step < totalSteps ? "var(--border)" : "none" }} />
              </div>
            </div>
          </div>
        </form>
      </section>

      {/* Bottom CTA */}
      <section className="dark-section" style={{ marginTop: 0 }}>
        <div className="container text-center">
          <h2 style={{ fontSize: 32, fontWeight: 800, textTransform: "uppercase", color: "var(--yellow)", marginBottom: 12 }}>
            Already have an account?
          </h2>
          <p style={{ color: "#ccc", marginBottom: 24, fontSize: 16 }}>Log in to manage your ground listings and view booking analytics.</p>
          <div style={{ display: "flex", gap: 12, justifyContent: "center", flexWrap: "wrap" }}>
            <Link to="/login" search={{ role: "admin" }} className="neo-btn lg">Login to Dashboard →</Link>
            <Link to="/register" className="neo-btn lg outline" style={{ color: "var(--white)", borderColor: "var(--white)" }}>Create Account</Link>
          </div>
        </div>
      </section>
    </>
  );
}
