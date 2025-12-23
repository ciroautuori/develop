import { createContext, useContext, useState, useEffect } from "react";
import type { ReactNode } from "react";
import { usersApi, type UserProfile } from "../../lib/api";
import { logger } from "../../lib/logger";
import { useAuthStorage } from "../../hooks/useAuthStorage";

interface AuthContextType {
  user: UserProfile | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (token: string) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const { token, setToken: setStoredToken, removeToken } = useAuthStorage();
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const initAuth = async () => {
      if (token) {
        try {
          // Verify token by fetching profile
          const userProfile = await usersApi.getMe();
          setUser(userProfile);
          setIsLoading(false);
        } catch (error) {
          logger.error("Auth init failed", { error });
          logout();
          setIsLoading(false);
        }
      } else {
        setIsLoading(false);
      }
    };
    initAuth();
  }, [token]);

  const login = (newToken: string) => {
    setStoredToken(newToken);
  };

  const logout = () => {
    removeToken();
    setUser(null);
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: !!token,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
