export const setToken = (token: string, user: any) => {
  localStorage.setItem("vantage_token", token);
  localStorage.setItem("vantage_user", JSON.stringify(user));
};

export const getToken = () =>
  typeof window !== "undefined" ? localStorage.getItem("vantage_token") : null;

export const getUser = () => {
  if (typeof window === "undefined") return null;
  const u = localStorage.getItem("vantage_user");
  return u ? JSON.parse(u) : null;
};

export const logout = () => {
  localStorage.removeItem("vantage_token");
  localStorage.removeItem("vantage_user");
  localStorage.removeItem("vantage_brand_id");
  window.location.href = "/login";
};

export const isLoggedIn = () => !!getToken();
