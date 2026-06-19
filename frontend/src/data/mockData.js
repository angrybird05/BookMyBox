// Mock data for BookMyBox

const amenityList = ["Floodlights", "Parking", "Changing Room", "Cafeteria", "Live Scoring"];

export const grounds = [
  { id: "g1", name: "Sixer Arena", location: "Hitech City", city: "Hyderabad", price: 800, rating: 4.7, reviewCount: 184, amenities: ["Floodlights","Parking","Cafeteria","Live Scoring"], availableSlots: 8, totalSlots: 16, tag: "POPULAR", description: "Premium box cricket turf with LED floodlights, professional astro turf and netting on all sides. Perfect for corporate matches and friendly games.", openTime: "06:00", closeTime: "23:00", slotDuration: 60, gradient: "linear-gradient(135deg,#FFE500,#FF6B6B)", icon: "🏏" },
  { id: "g2", name: "PowerPlay Box", location: "Gachibowli", city: "Hyderabad", price: 1000, rating: 4.9, reviewCount: 232, amenities: ["Floodlights","Parking","Changing Room","Cafeteria","Live Scoring"], availableSlots: 3, totalSlots: 14, tag: "PREMIUM", description: "Top-rated venue with international-standard turf, live streaming and a full cafeteria.", openTime: "06:00", closeTime: "23:00", slotDuration: 60, gradient: "linear-gradient(135deg,#4ECDC4,#B388FF)", icon: "🎯" },
  { id: "g3", name: "Boundary Hitters", location: "Kondapur", city: "Hyderabad", price: 600, rating: 4.4, reviewCount: 96, amenities: ["Floodlights","Parking"], availableSlots: 11, totalSlots: 16, tag: "NEW", description: "Budget-friendly box cricket ground with great turf quality.", openTime: "07:00", closeTime: "22:00", slotDuration: 60, gradient: "linear-gradient(135deg,#69F0AE,#FFE500)", icon: "⚡" },
  { id: "g4", name: "Yorker Zone", location: "Madhapur", city: "Hyderabad", price: 900, rating: 4.6, reviewCount: 145, amenities: ["Floodlights","Cafeteria","Live Scoring"], availableSlots: 6, totalSlots: 16, tag: "POPULAR", description: "Bowler-friendly turf with practice nets and a coaching area.", openTime: "06:00", closeTime: "23:00", slotDuration: 60, gradient: "linear-gradient(135deg,#B388FF,#FF6B6B)", icon: "🔥" },
  { id: "g5", name: "Cover Drive Cricket", location: "Banjara Hills", city: "Hyderabad", price: 1200, rating: 4.8, reviewCount: 201, amenities: amenityList, availableSlots: 4, totalSlots: 14, tag: "PREMIUM", description: "Elite venue with rooftop seating, live commentary and HD recording.", openTime: "06:00", closeTime: "24:00", slotDuration: 60, gradient: "linear-gradient(135deg,#FF6B6B,#FFE500)", icon: "👑" },
  { id: "g6", name: "Stumps & Wickets", location: "Kukatpally", city: "Hyderabad", price: 500, rating: 4.2, reviewCount: 64, amenities: ["Parking","Changing Room"], availableSlots: 12, totalSlots: 16, tag: "NEW", description: "Affordable neighbourhood box cricket ground.", openTime: "07:00", closeTime: "22:00", slotDuration: 60, gradient: "linear-gradient(135deg,#4ECDC4,#FFE500)", icon: "🏟️" },
  { id: "g7", name: "Helmet Heroes Arena", location: "Miyapur", city: "Hyderabad", price: 700, rating: 4.5, reviewCount: 118, amenities: ["Floodlights","Parking","Cafeteria"], availableSlots: 9, totalSlots: 16, tag: "POPULAR", description: "Friendly turf with snack counter and ample parking.", openTime: "06:00", closeTime: "23:00", slotDuration: 60, gradient: "linear-gradient(135deg,#69F0AE,#4ECDC4)", icon: "⛑️" },
  { id: "g8", name: "Cricket Cage 360", location: "Jubilee Hills", city: "Hyderabad", price: 1100, rating: 4.7, reviewCount: 173, amenities: amenityList, availableSlots: 5, totalSlots: 14, tag: "PREMIUM", description: "Fully caged premium ground with smart booking kiosks.", openTime: "06:00", closeTime: "24:00", slotDuration: 60, gradient: "linear-gradient(135deg,#FFE500,#B388FF)", icon: "🎪" },
];

export function getGround(id) { return grounds.find(g => g.id === id); }

export function generateSlots(groundId, date) {
  const ground = getGround(groundId);
  if (!ground) return [];
  const slots = [];
  // seed by groundId+date for stable randomness
  let seed = 0; for (const c of (groundId + date)) seed = (seed * 31 + c.charCodeAt(0)) >>> 0;
  const rand = () => { seed = (seed * 1664525 + 1013904223) >>> 0; return seed / 0xffffffff; };
  for (let h = 6; h < 23; h++) {
    const id = `${groundId}-${date}-${h}`;
    const startTime = `${String(h).padStart(2,'0')}:00`;
    const endTime = `${String(h+1).padStart(2,'0')}:00`;
    const status = rand() < 0.3 ? "booked" : "available";
    slots.push({ id, groundId, date, startTime, endTime, price: ground.price, status, duration: 60 });
  }
  return slots;
}

export const bookings = [
  { id: "b1", ref: "BMB-2026-48201", groundId: "g1", groundName: "Sixer Arena", date: "2026-06-22", slots: [{ startTime:"18:00", endTime:"19:00", price:800 },{ startTime:"19:00", endTime:"20:00", price:800 }], totalAmount: 1600, discount: 0, finalAmount: 1600, status: "CONFIRMED", createdAt: "2026-06-15" },
  { id: "b2", ref: "BMB-2026-48305", groundId: "g2", groundName: "PowerPlay Box", date: "2026-06-25", slots: [{ startTime:"20:00", endTime:"21:00", price:1000 },{ startTime:"21:00", endTime:"22:00", price:1000 },{ startTime:"22:00", endTime:"23:00", price:1000 }], totalAmount: 3000, discount: 300, finalAmount: 2700, status: "CONFIRMED", createdAt: "2026-06-14" },
  { id: "b3", ref: "BMB-2026-47119", groundId: "g3", groundName: "Boundary Hitters", date: "2026-06-10", slots: [{ startTime:"17:00", endTime:"18:00", price:600 }], totalAmount: 600, discount: 0, finalAmount: 600, status: "COMPLETED", createdAt: "2026-06-05" },
  { id: "b4", ref: "BMB-2026-46902", groundId: "g4", groundName: "Yorker Zone", date: "2026-05-28", slots: [{ startTime:"19:00", endTime:"20:00", price:900 }], totalAmount: 900, discount: 0, finalAmount: 900, status: "COMPLETED", createdAt: "2026-05-22" },
  { id: "b5", ref: "BMB-2026-46550", groundId: "g5", groundName: "Cover Drive Cricket", date: "2026-05-15", slots: [{ startTime:"20:00", endTime:"21:00", price:1200 }], totalAmount: 1200, discount: 0, finalAmount: 1200, status: "CANCELLED", createdAt: "2026-05-12" },
];

export const users = [
  { id: "u1", name: "Pavan Kumar", email: "user@bookmybox.com", password: "password123", phone: "+91 98765 43210", city: "Hyderabad", role: "user", wallet: 1250, totalSpent: 8400, bookings: 12, status: "ACTIVE" },
  { id: "u2", name: "Anil Verma", email: "anil@bookmybox.com", password: "password123", phone: "+91 99887 12345", city: "Bengaluru", role: "user", wallet: 500, totalSpent: 4200, bookings: 6, status: "ACTIVE" },
  { id: "u3", name: "Admin Singh", email: "admin@bookmybox.com", password: "admin123", phone: "+91 99000 11111", city: "Hyderabad", role: "admin", wallet: 0, totalSpent: 0, bookings: 0, status: "ACTIVE" },
];

export const reviews = [
  { id: "r1", user: "Rohit S.", rating: 5, text: "Top notch turf and floodlights. Booked 3 slots, got 10% off. Smooth experience!" },
  { id: "r2", user: "Priya M.", rating: 5, text: "Booking 4 slots for our office tournament was so easy. Loved the cart flow." },
  { id: "r3", user: "Karthik R.", rating: 4, text: "Great ground, parking was a bit tight on a Saturday night but turf was perfect." },
  { id: "r4", user: "Sneha T.", rating: 5, text: "Used the partial cancellation to refund one slot. Worked flawlessly." },
  { id: "r5", user: "Vikram J.", rating: 4, text: "Fast booking, no hidden charges. Will return." },
  { id: "r6", user: "Meera P.", rating: 5, text: "Best box cricket platform in the city. Period." },
];

export const adminStats = {
  totalRevenue: 482300,
  totalBookings: 1284,
  activeGrounds: 8,
  activeUsers: 2104,
  todayBookings: 47,
  pendingCancellations: 3,
};
