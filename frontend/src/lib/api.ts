// API client for BookMyBox connecting to the FastAPI backend

const DEFAULT_API_URL = "http://localhost:8000/api/v1";

export const getApiUrl = () => {
  // Try loading from import.meta.env (Vite)
  try {
    const envUrl = import.meta.env.VITE_API_URL;
    if (envUrl) return envUrl;
  } catch {}
  return DEFAULT_API_URL;
};

// Local storage keys
const ACCESS_TOKEN_KEY = "bmb_access_token";
const REFRESH_TOKEN_KEY = "bmb_refresh_token";
const USER_KEY = "bmb_user";

// Token helpers
export const getAccessToken = () => {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(ACCESS_TOKEN_KEY);
};

export const getRefreshToken = () => {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(REFRESH_TOKEN_KEY);
};

export const setTokens = (accessToken: string, refreshToken: string) => {
  if (typeof window === "undefined") return;
  localStorage.setItem(ACCESS_TOKEN_KEY, accessToken);
  localStorage.setItem(REFRESH_TOKEN_KEY, refreshToken);
};

export const clearAuthData = () => {
  if (typeof window === "undefined") return;
  localStorage.removeItem(ACCESS_TOKEN_KEY);
  localStorage.removeItem(REFRESH_TOKEN_KEY);
  localStorage.removeItem(USER_KEY);
};

// Central fetch wrapper
async function request(path: string, options: RequestInit = {}) {
  const url = `${getApiUrl()}${path}`;
  const token = getAccessToken();

  const headers = new Headers(options.headers || {});
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }
  if (!headers.has("Content-Type") && !(options.body instanceof FormData)) {
    headers.set("Content-Type", "application/json");
  }

  const response = await fetch(url, {
    ...options,
    headers,
  });

  // Handle 401 token refresh (optional implementation)
  if (response.status === 401) {
    // If we're not already on the login page or trying to refresh/login
    if (!path.includes("/auth/login") && !path.includes("/auth/refresh")) {
      const refresh = getRefreshToken();
      if (refresh) {
        try {
          const refreshRes = await fetch(`${getApiUrl()}/auth/refresh`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ refresh_token: refresh }),
          });
          if (refreshRes.ok) {
            const data = await refreshRes.json();
            if (data.status === "success" && data.data) {
              setTokens(data.data.access_token, data.data.refresh_token);
              // Retry original request
              headers.set("Authorization", `Bearer ${data.data.access_token}`);
              const retryResponse = await fetch(url, { ...options, headers });
              return await handleResponse(retryResponse);
            }
          }
        } catch {
          clearAuthData();
        }
      }
      clearAuthData();
    }
  }

  return await handleResponse(response);
}

async function handleResponse(response: Response) {
  // If download ticket (PDF response)
  const contentType = response.headers.get("content-type") || "";
  if (contentType.includes("application/pdf")) {
    return response.blob();
  }

  const json = await response.json();
  if (!response.ok) {
    const errorMsg = json.message || "An error occurred";
    const error = new Error(errorMsg) as any;
    error.status = response.status;
    error.errors = json.errors;
    throw error;
  }

  return json;
}

// Auth API Endpoints
export const apiLogin = async (loginData: any) => {
  const res = await request("/auth/login", {
    method: "POST",
    body: JSON.stringify(loginData),
  });
  if (res.status === "success" && res.data) {
    setTokens(res.data.tokens.access_token, res.data.tokens.refresh_token);
    localStorage.setItem(USER_KEY, JSON.stringify(res.data.user));
  }
  return res.data;
};

export const apiRegister = async (registerData: any) => {
  return await request("/auth/register", {
    method: "POST",
    body: JSON.stringify(registerData),
  });
};

export const apiVerifyOtp = async (email: string, otpCode: string) => {
  const res = await request("/auth/verify-otp", {
    method: "POST",
    body: JSON.stringify({ email, otp_code: otpCode }),
  });
  if (res.status === "success" && res.data) {
    setTokens(res.data.tokens.access_token, res.data.tokens.refresh_token);
    localStorage.setItem(USER_KEY, JSON.stringify(res.data.user));
  }
  return res.data;
};

export const apiLogout = async () => {
  const refresh = getRefreshToken();
  if (refresh) {
    try {
      await request("/auth/logout", {
        method: "POST",
        body: JSON.stringify({ refresh_token: refresh }),
      });
    } catch {}
  }
  clearAuthData();
};

export const apiGetMe = async () => {
  const res = await request("/users/me");
  if (res.status === "success") {
    localStorage.setItem(USER_KEY, JSON.stringify(res.data));
  }
  return res.data;
};

export const apiGetMeStats = async () => {
  const res = await request("/users/me/stats");
  return res.data;
};

export const apiUpdateMe = async (profileData: any) => {
  const res = await request("/users/me", {
    method: "PUT",
    body: JSON.stringify(profileData),
  });
  if (res.status === "success") {
    localStorage.setItem(USER_KEY, JSON.stringify(res.data));
  }
  return res.data;
};

// Grounds API Endpoints
export const apiGetGrounds = async (filters: any = {}) => {
  const params = new URLSearchParams();
  if (filters.city) params.set("city", filters.city);
  if (filters.search) params.set("search", filters.search);
  if (filters.price_min) params.set("price_min", filters.price_min);
  if (filters.price_max) params.set("price_max", filters.price_max);
  if (filters.tag) params.set("tag", filters.tag);
  if (filters.sort_by) params.set("sort_by", filters.sort_by);
  if (filters.page) params.set("page", filters.page.toString());
  if (filters.per_page) params.set("per_page", filters.per_page.toString());
  if (filters.amenities && filters.amenities.length) {
    filters.amenities.forEach((a: string) => params.append("amenities", a));
  }

  const query = params.toString() ? `?${params.toString()}` : "";
  return await request(`/grounds${query}`);
};

export const apiGetTopGrounds = async (limit = 6) => {
  const res = await request(`/grounds/top?limit=${limit}`);
  return res.data;
};

export const apiGetGround = async (id: string) => {
  const res = await request(`/grounds/${id}`);
  return res.data;
};

export const apiGetSlots = async (id: string, date: string) => {
  const res = await request(`/grounds/${id}/slots?date=${date}`);
  return res.data;
};

export const apiGetReviews = async (id: string, page = 1, perPage = 10) => {
  return await request(`/grounds/${id}/reviews?page=${page}&per_page=${perPage}`);
};

// Bookings API Endpoints
export const apiCreateBooking = async (bookingData: {
  ground_id: string;
  booking_date: string;
  slot_ids: string[];
  promo_code?: string;
  payment_method: string;
}) => {
  const res = await request("/bookings", {
    method: "POST",
    body: JSON.stringify(bookingData),
  });
  return res.data;
};

export const apiGetMyBookings = async (tab?: string, page = 1, perPage = 10) => {
  const query = `?page=${page}&per_page=${perPage}${tab ? `&tab=${tab}` : ""}`;
  return await request(`/bookings${query}`);
};

export const apiGetBooking = async (id: string) => {
  const res = await request(`/bookings/${id}`);
  return res.data;
};

export const apiCancelBooking = async (id: string) => {
  const res = await request(`/bookings/${id}/cancel`, {
    method: "POST",
  });
  return res.data;
};

export const apiCancelSpecificSlots = async (id: string, slotIds: string[]) => {
  const res = await request(`/bookings/${id}/cancel-slots`, {
    method: "POST",
    body: JSON.stringify({ slot_ids: slotIds }),
  });
  return res.data;
};

export const apiValidatePromo = async (code: string, totalAmount: number) => {
  const res = await request("/bookings/validate-promo", {
    method: "POST",
    body: JSON.stringify({ code, total_amount: totalAmount }),
  });
  return res.data;
};

export const apiDownloadTicket = async (id: string) => {
  return await request(`/bookings/${id}/ticket`);
};

// Wallet API Endpoints
export const apiGetWalletBalance = async () => {
  const res = await request("/wallet");
  return res.data;
};

export const apiTopUpWallet = async (amount: number) => {
  const res = await request("/wallet/topup", {
    method: "POST",
    body: JSON.stringify({ amount }),
  });
  return res.data;
};

export const apiGetWalletTransactions = async (page = 1, perPage = 10) => {
  return await request(`/wallet/transactions?page=${page}&per_page=${perPage}`);
};

// Admin API Endpoints
export const apiAdminGetStats = async () => {
  const res = await request("/admin/stats");
  return res.data;
};

export const apiAdminGetRevenueChart = async () => {
  const res = await request("/admin/revenue-chart");
  return res.data;
};

export const apiAdminCreateGround = async (groundData: any) => {
  const res = await request("/admin/grounds", {
    method: "POST",
    body: JSON.stringify(groundData),
  });
  return res.data;
};

export const apiAdminUpdateGround = async (id: string, groundData: any) => {
  const res = await request(`/admin/grounds/${id}`, {
    method: "PUT",
    body: JSON.stringify(groundData),
  });
  return res.data;
};

export const apiAdminToggleGroundStatus = async (id: string, isActive: boolean) => {
  const res = await request(`/admin/grounds/${id}/status?is_active=${isActive}`, {
    method: "PATCH",
  });
  return res.data;
};

export const apiAdminDeleteGround = async (id: string) => {
  const res = await request(`/admin/grounds/${id}`, {
    method: "DELETE",
  });
  return res.data;
};

export const apiAdminGetSlots = async (groundId: string, date: string) => {
  const res = await request(`/admin/grounds/${groundId}/slots?date=${date}`);
  return res.data;
};

export const apiAdminBlockSlots = async (slotIds: string[]) => {
  const res = await request("/admin/slots/block", {
    method: "POST",
    body: JSON.stringify({ slot_ids: slotIds }),
  });
  return res.data;
};

export const apiAdminUnblockSlots = async (slotIds: string[]) => {
  const res = await request("/admin/slots/unblock", {
    method: "POST",
    body: JSON.stringify({ slot_ids: slotIds }),
  });
  return res.data;
};

export const apiAdminBulkUpdateSlotPrices = async (slotIds: string[], price: number) => {
  const res = await request("/admin/slots/price", {
    method: "PUT",
    body: JSON.stringify({ slot_ids: slotIds, price }),
  });
  return res.data;
};

export const apiAdminGetBookings = async (search?: string, statusFilter?: string, page = 1, perPage = 10) => {
  let query = `?page=${page}&per_page=${perPage}`;
  if (search) query += `&search=${encodeURIComponent(search)}`;
  if (statusFilter) query += `&status=${statusFilter}`;
  return await request(`/admin/bookings${query}`);
};

export const apiAdminCancelBooking = async (id: string) => {
  const res = await request(`/admin/bookings/${id}/cancel`, {
    method: "POST",
  });
  return res.data;
};

export const apiAdminGetUsers = async (search?: string, page = 1, perPage = 10) => {
  let query = `?page=${page}&per_page=${perPage}`;
  if (search) query += `&search=${encodeURIComponent(search)}`;
  return await request(`/admin/users${query}`);
};

export const apiAdminToggleUserBlock = async (id: string, statusVal: string) => {
  const res = await request(`/admin/users/${id}/status?status=${statusVal}`, {
    method: "PATCH",
  });
  return res.data;
};

export const apiGetFeaturedReviews = async (limit = 5) => {
  const res = await request(`/reviews/featured?limit=${limit}`);
  return res.data;
};

