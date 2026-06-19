import { createContext, useContext, useEffect, useMemo, useState } from "react";

/** @type {React.Context<any>} */
const BookingContext = createContext(null);
const KEY = "bmb_booking";

export function BookingProvider({ children }) {
  const [selectedGround, setSelectedGround] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedSlots, setSelectedSlots] = useState([]);

  useEffect(() => {
    try {
      const raw = typeof window !== "undefined" ? sessionStorage.getItem(KEY) : null;
      if (raw) {
        const v = JSON.parse(raw);
        setSelectedGround(v.selectedGround || null);
        setSelectedDate(v.selectedDate || null);
        setSelectedSlots(v.selectedSlots || []);
      }
    } catch {}
  }, []);

  useEffect(() => {
    try { sessionStorage.setItem(KEY, JSON.stringify({ selectedGround, selectedDate, selectedSlots })); } catch {}
  }, [selectedGround, selectedDate, selectedSlots]);

  const addSlot = (slot) => setSelectedSlots(s => s.find(x => x.id === slot.id) ? s : [...s, slot]);
  const removeSlot = (id) => setSelectedSlots(s => s.filter(x => x.id !== id));
  const clearSlots = () => setSelectedSlots([]);

  const totals = useMemo(() => {
    const subtotal = selectedSlots.reduce((a, s) => a + s.price, 0);
    const discount = selectedSlots.length >= 3 ? Math.round(subtotal * 0.1) : 0;
    return { subtotal, discount, total: subtotal - discount };
  }, [selectedSlots]);

  return (
    <BookingContext.Provider value={{
      selectedGround, setSelectedGround,
      selectedDate, setSelectedDate,
      selectedSlots, addSlot, removeSlot, clearSlots,
      ...totals,
    }}>
      {children}
    </BookingContext.Provider>
  );
}

export function useBooking() {
  const ctx = useContext(BookingContext);
  if (!ctx) throw new Error("useBooking must be used inside BookingProvider");
  return ctx;
}
