import { create } from "zustand";
import { api } from "../services/api";

interface AuthState {
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  logout: () => void;
  refresh: () => Promise<boolean>;
  clearError: () => void;
  initialize: () => void;
}

interface TokenResponse {
  access_token: string;
  refresh_token: string;
}

export const useAuthStore = create<AuthState>((set, get) => ({
  accessToken: null,
  refreshToken: null,
  isAuthenticated: false,
  isLoading: false,
  error: null,

  initialize: () => {
    const accessToken = localStorage.getItem("access_token");
    const refreshToken = localStorage.getItem("refresh_token");
    if (accessToken) {
      set({ accessToken, refreshToken, isAuthenticated: true });
    }
  },

  login: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await api.post<TokenResponse>("/auth/login", { email, password });
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      set({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch {
      set({ isLoading: false, error: "Invalid email or password" });
    }
  },

  register: async (email: string, password: string) => {
    set({ isLoading: true, error: null });
    try {
      const data = await api.post<TokenResponse>("/auth/register", { email, password });
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      set({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        isAuthenticated: true,
        isLoading: false,
      });
    } catch {
      set({ isLoading: false, error: "Registration failed. Email may already be in use." });
    }
  },

  logout: () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    set({
      accessToken: null,
      refreshToken: null,
      isAuthenticated: false,
    });
  },

  refresh: async () => {
    const { refreshToken } = get();
    if (!refreshToken) return false;
    try {
      const data = await api.post<TokenResponse>("/auth/refresh", {
        refresh_token: refreshToken,
      });
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("refresh_token", data.refresh_token);
      set({
        accessToken: data.access_token,
        refreshToken: data.refresh_token,
        isAuthenticated: true,
      });
      return true;
    } catch {
      get().logout();
      return false;
    }
  },

  clearError: () => set({ error: null }),
}));
