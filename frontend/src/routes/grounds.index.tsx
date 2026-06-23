import { useState, useEffect } from "react";
import { createFileRoute } from "@tanstack/react-router";
import { apiGetGrounds } from "../lib/api";
import GroundCard from "../components/GroundCard";

export const Route = createFileRoute("/grounds/")({
  head: () => ({ meta: [{ title: "Browse Grounds — BookMyBox" }, { name: "description", content: "Browse box cricket grounds, filter by price, amenities and rating." }] }),
  component: GroundsPage,
});

function GroundsPage() {
  const [groundsList, setGroundsList] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [totalCount, setTotalCount] = useState(0);

  const [location, setLocation] = useState("");
  const [minPrice, setMinPrice] = useState("");
  const [maxPrice, setMaxPrice] = useState("");
  const [amenities, setAmenities] = useState<string[]>([]);
  const [minRating, setMinRating] = useState(0);
  const [sort, setSort] = useState("rating");
  const [page, setPage] = useState(1);
  const perPage = 10;

  useEffect(() => {
    async function fetchGrounds() {
      setLoading(true);
      try {
        const filters: any = {
          search: location || undefined,
          price_min: minPrice ? parseInt(minPrice) : undefined,
          price_max: maxPrice ? parseInt(maxPrice) : undefined,
          amenities: amenities.length ? amenities : undefined,
          page,
          per_page: perPage,
        };
        
        if (sort === "rating") filters.sort_by = "rating_desc";
        else if (sort === "price-asc") filters.sort_by = "price_asc";
        else if (sort === "price-desc") filters.sort_by = "price_desc";

        const res = await apiGetGrounds(filters);
        if (res && res.data) {
          // If ground rating filter is checked, filter client-side as well if server-side doesn't support direct rating bounds
          let data = res.data;
          if (minRating > 0) {
            data = data.filter((g: any) => g.rating >= minRating);
          }
          setGroundsList(data);
          setTotalCount(res.meta?.total || data.length);
        }
      } catch (err) {
        console.error("Error fetching grounds:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchGrounds();
  }, [location, minPrice, maxPrice, amenities, minRating, sort, page]);

  const toggleAmenity = (a: string) => setAmenities(s => s.includes(a) ? s.filter(x => x !== a) : [...s, a]);
  const reset = () => { setLocation(""); setMinPrice(""); setMaxPrice(""); setAmenities([]); setMinRating(0); setPage(1); };

  const totalPages = Math.max(1, Math.ceil(totalCount / perPage));

  return (
    <div className="container listing-layout">
      <aside className="filters">
        <h3 style={{ textTransform: "uppercase", fontWeight: 800, marginBottom: 12 }}>Filter Grounds</h3>
        <div className="filter-group">
          <h4>Location</h4>
          <input className="neo-input" placeholder="City / area" value={location} onChange={e => { setLocation(e.target.value); setPage(1); }} />
        </div>
        <div className="filter-group">
          <h4>Price Range</h4>
          <div className="form-row">
            <input className="neo-input" placeholder="₹ Min" value={minPrice} onChange={e => { setMinPrice(e.target.value); setPage(1); }} />
            <input className="neo-input" placeholder="₹ Max" value={maxPrice} onChange={e => { setMaxPrice(e.target.value); setPage(1); }} />
          </div>
        </div>
        <div className="filter-group">
          <h4>Amenities</h4>
          {["Floodlights","Parking","Changing Room","Cafeteria","Live Scoring"].map(a => (
            <label key={a}><input type="checkbox" checked={amenities.includes(a)} onChange={() => { toggleAmenity(a); setPage(1); }} /> {a}</label>
          ))}
        </div>
        <div className="filter-group">
          <h4>Rating</h4>
          {[4, 3, 0].map(r => (
            <label key={r}><input type="radio" name="rating" checked={minRating === r} onChange={() => { setMinRating(r); setPage(1); }} /> {r ? `${r}★ & above` : "All"}</label>
          ))}
        </div>
        <button onClick={reset} style={{ display: "block", margin: "12px auto 0", fontWeight: 700, color: "var(--coral)", textTransform: "uppercase", fontSize: 12 }}>Clear All</button>
      </aside>

      <div>
        <div className="listing-top">
          <div style={{ fontWeight: 700 }}>Showing {groundsList.length} grounds</div>
          <select className="neo-input" style={{ width: "auto" }} value={sort} onChange={e => { setSort(e.target.value); setPage(1); }}>
            <option value="rating">Top Rated</option>
            <option value="price-asc">Price: Low → High</option>
            <option value="price-desc">Price: High → Low</option>
          </select>
        </div>
        
        {loading ? (
          <div className="neo-card text-center" style={{ padding: 40 }}>Loading grounds...</div>
        ) : (
          <>
            <div className="ground-grid">
              {groundsList.map(g => <GroundCard key={g.id} g={g} />)}
            </div>
            {groundsList.length === 0 && <div className="neo-card text-center">No grounds match these filters.</div>}
            
            {totalPages > 1 && (
              <div className="flex gap-2 mt-8" style={{ justifyContent: "center" }}>
                {Array.from({ length: totalPages }, (_, i) => i + 1).map(n => (
                  <button key={n} onClick={() => setPage(n)} className={`neo-btn sm ${n !== page ? "outline" : ""}`}>{n}</button>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
