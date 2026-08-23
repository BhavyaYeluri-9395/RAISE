import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import axios from "axios";

const AuthContext = createContext(null);

const API_URL =
  import.meta.env.VITE_API_URL ||
  "http://127.0.0.1:8000";

const api = axios.create({
  baseURL: API_URL,
  timeout: 10000,
});

export function AuthProvider({ children }) {

  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  // ============================================================
  // CHECK EXISTING LOGIN
  // ============================================================

  useEffect(() => {

    const token =
      localStorage.getItem("raise_token");

    if (!token) {
      setLoading(false);
      return;
    }

    api
      .get("/auth/me", {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      })
      .then((response) => {

        setUser(response.data);

      })
      .catch(() => {

        localStorage.removeItem("raise_token");
        setUser(null);

      })
      .finally(() => {

        setLoading(false);

      });

  }, []);

  // ============================================================
  // LOGIN
  // ============================================================

  const login = async (
    email,
    password
  ) => {

    const response = await api.post(
      "/auth/login",
      {
        email,
        password,
      }
    );

    const {
      access_token,
      user,
    } = response.data;

    localStorage.setItem(
      "raise_token",
      access_token
    );

    setUser(user);

    return user;
  };

  // ============================================================
  // REGISTER
  // ============================================================

  const register = async (
    fullName,
    email,
    password,
    role
  ) => {

    const response = await api.post(
      "/auth/register",
      {
        full_name: fullName,
        email,
        password,
        role,
      }
    );

    return response.data;
  };

  // ============================================================
  // LOGOUT
  // ============================================================

  const logout = () => {

    localStorage.removeItem(
      "raise_token"
    );

    setUser(null);
  };

  // ============================================================
  // CONTEXT
  // ============================================================

  const value = {
    user,
    loading,
    login,
    register,
    logout,
    isAuthenticated: !!user,
  };

  return (
    <AuthContext.Provider value={value}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {

  return useContext(AuthContext);
}