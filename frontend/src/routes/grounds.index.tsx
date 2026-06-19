import { useState, useMemo } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { grounds } from "../data/mockData";
import GroundCard from "../components/GroundCard";

export const Route = createFileRoute("/grounds/")({
  head: () => ({ meta: [{ title: "Browse Grounds — BookMyBox" }, { name: "description", content: "Browse box cricket grounds, filter by price, amenities and rating." }] }),
  component: GroundsPage,
});

function GroundsPage() {
  const [location, setLocation] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [amenities, setAmenities] = useState<string[]>([]);
  const [minRating, setMinRating] = useState(0);
  const [sort, setSort] = useState("rating");

  const filtered = useMemo(() => {
    let list = grounds.filter(g => {
      if (location && !`${g.location} ${g.city}`.toLowerCase().includes(location.toLowerCase())) return false;
      if (minPrice && g.price < +minPrice) return false;
      if (maxPrice && g.price > +maxPrice) return false;
      if (amenities.length && !amenities.every(a => g.amenities.includes(a))) return false;
      if (g.rating < minRating) return false;
      return true;
    });
    if (sort === "price-asc") list = [...list].sort((a, b) => a.price - b.price);
    if (sort === "price-desc") list = [...list].sort((a, b) => b.price - a.price);
    if (sort === "rating") list = [...list].sort((a, b) => b.rating - a.rating);
    return list;
  }, [location, minPrice, maxPrice, amenities, minRating, sort]);

  const toggleAmenity = (a: string) => setAmenities(s => s.includes(a) ? s.filter(x => x !== a) : [...s, a]);
  const reset = () => { setLocation(""); setMinPrice(""); setMaxPrice(""); setAmenities([]); setMinRating(0); };

  return (
    <div className="container listing-layout">
      <aside className="filters">
        <h3 style={{ textTransform: "uppercase", fontWeight: 800, marginBottom: 12 }}>Filter Grounds</h3>
        <div className="filter-group">
          <h4>Location</h4>
          <input className="neo-input" placeholder="City / area" value={location} onChange={e => setLocation(e.target.value)} />
        </div>
        <div className="filter-group">
          <h4>Date</h4>
          <input className="neo-input" type="date" />
        </div>
        <div className="filter-group">
          <h4>Price Range</h4>
          <div className="form-row">
            <input className="neo-input" placeholder="₹ Min" value={minPrice} onChange={e => setMinPrice(e.target.value)} />
            <input className="neo-input" placeholder="₹ Max" value={maxPrice} onChange={e => setMaxPrice(e.target.value)} />
          </div>
        </div>
        <div className="filter-group">
          <h4>Amenities</h4>
          {["Floodlights","Parking","Changing Room","Cafeteria","Live Scoring"].map(a => (
            <label key={a}><input type="checkbox" checked={amenities.includes(a)} onChange={() => toggleAmenity(a)} /> {a}</label>
          ))}
        </div>
        <div className="filter-group">
          <h4>Rating</h4>
          {[4, 3, 0].map(r => (
            <label key={r}><input type="radio" name="rating" checked={minRating === r} onChange={() => setMinRating(r)} /> {r ? `${r}★ & above` : "All"}</label>
          ))}
        </div>
        <button className="neo-btn block mt-4">Apply Filters</button>
        <button onClick={reset} style={{ display: "block", margin: "12px auto 0", fontWeight: 700, color: "var(--coral)", textTransform: "uppercase", fontSize: 12 }}>Clear All</button>
      </aside>

      <div>
        <div className="listing-top">
          <div style={{ fontWeight: 700 }}>Showing {filtered.length} grounds</div>
          <select className="neo-input" style={{ width: "auto" }} value={sort} onChange={e => setSort(e.target.value)}>
            <option value="rating">Top Rated</option>
            <option value="price-asc">Price: Low → High</option>
            <option value="price-desc">Price: High → Low</option>
          </select>
        </div>
        <div className="ground-grid">
          {filtered.map(g => <GroundCard key={g.id} g={g} />)}
        </div>
        {filtered.length === 0 && <div className="neo-card text-center">No grounds match these filters.</div>}
        <div className="flex gap-2 mt-8" style={{ justifyContent: "center" }}>
          {[1,2,3].map(n => <button key={n} className={`neo-btn sm ${n!==1 ? "outline" : ""}`}>{n}</button>)}
          <button className="neo-btn sm outline">→</button>
        </div>
      </div>
    </div>
  );
}
