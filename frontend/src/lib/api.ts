import axios from "axios";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const api = axios.create({ baseURL: API_URL });

// Attach token automatically
api.interceptors.request.use((config) => {
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("vantage_token");
    if (token) config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Auth
export const login = (email: string, password: string) =>
  api.post("/api/auth/login", { email, password });

export const register = (name: string, email: string, password: string) =>
  api.post("/api/auth/register", { name, email, password });

// Brands
export const getBrands = () => api.get("/api/brands");
export const createBrand = (data: any) => api.post("/api/brands", data);
export const getDashboard = (brandId: string) => api.get(`/api/brands/${brandId}/dashboard`);

// Competitors
export const getCompetitors = (brandId: string) => api.get(`/api/brands/${brandId}/competitors`);
export const addCompetitor = (brandId: string, data: any) => api.post(`/api/brands/${brandId}/competitors`, data);
export const removeCompetitor = (brandId: string, competitorId: string) =>
  api.delete(`/api/brands/${brandId}/competitors/${competitorId}`);
export const syncCompetitor = (brandId: string, competitorId: string) =>
  api.post(`/api/brands/${brandId}/competitors/${competitorId}/sync`);

// Ads
export const getAds = (brandId: string, params?: any) => api.get(`/api/brands/${brandId}/ads`, { params });

// Briefs
export const getBriefs = (brandId: string) => api.get(`/api/brands/${brandId}/briefs`);
export const getLatestBrief = (brandId: string) => api.get(`/api/brands/${brandId}/briefs/latest`);
export const getBrief = (briefId: string) => api.get(`/api/briefs/${briefId}`);
export const generateBrief = (brandId: string) => api.post(`/api/brands/${brandId}/briefs/generate`);

// Alerts
export const getAlerts = (brandId: string) => api.get(`/api/brands/${brandId}/alerts`);
export const markAlertRead = (alertId: string) => api.put(`/api/alerts/${alertId}/read`);

export default api;
