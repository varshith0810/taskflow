import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { auth } from '../api/client';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const loadUser = useCallback(async () => {
    const token = localStorage.getItem('access_token');
    if (!token) { setLoading(false); return; }
    try {
      const me = await auth.me();
      setUser(me);
    } catch {
      setUser(null);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadUser();
    const onLogout = () => setUser(null);
    window.addEventListener('auth:logout', onLogout);
    return () => window.removeEventListener('auth:logout', onLogout);
  }, [loadUser]);

  const login = async (credentials) => {
    await auth.login(credentials);
    const me = await auth.me();
    setUser(me);
    return me;
  };

  const logout = () => {
    auth.logout();
    setUser(null);
  };

  const signup = async (data) => {
    await auth.signup(data);
    return login({ email: data.email, password: data.password });
  };

  return (
    <AuthContext.Provider value={{ user, loading, login, logout, signup, reload: loadUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
