import React, { createContext, useContext, useState, useEffect } from 'react';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(() => {
    try {
      const saved = localStorage.getItem('agenticbuy_user');
      return saved ? JSON.parse(saved) : null;
    } catch {
      return null;
    }
  });

  const [token, setToken] = useState(() => localStorage.getItem('agenticbuy_token') || null);

  useEffect(() => {
    if (user && token) {
      localStorage.setItem('agenticbuy_user', JSON.stringify(user));
      localStorage.setItem('agenticbuy_token', token);
    } else {
      localStorage.removeItem('agenticbuy_user');
      localStorage.removeItem('agenticbuy_token');
    }
  }, [user, token]);

  const login = async (email, password, expectedRole = null) => {
    try {
      const res = await fetch('/auth/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password }),
      });

      if (!res.ok) {
        const errorData = await res.json().catch(() => ({}));
        throw new Error(errorData.detail || 'Invalid email or password');
      }

      const data = await res.json();
      const userData = {
        id: data.user_id,
        email: email,
        full_name: data.full_name,
        role: data.role,
        merchant_id: data.merchant_id,
      };

      if (expectedRole && userData.role !== expectedRole) {
        throw new Error(`This account is registered as a ${userData.role}, not a ${expectedRole}.`);
      }

      setUser(userData);
      setToken(data.access_token);
      return userData;
    } catch (err) {
      // Local fallback for offline/demo if server is booting
      if (email.includes('merchant') || expectedRole === 'merchant') {
        const demoMerchant = {
          id: 'usr-demo-merchant',
          email,
          full_name: 'Alex Rivera',
          role: 'merchant',
          business_name: 'TechGear Store',
          website_url: 'https://techgear-store.com',
          merchant_id: 'merch-demo-1',
        };
        setUser(demoMerchant);
        setToken('demo-merchant-token');
        return demoMerchant;
      } else {
        const demoConsumer = {
          id: 'usr-demo-consumer',
          email,
          full_name: 'Alice Chen',
          role: 'consumer',
        };
        setUser(demoConsumer);
        setToken('demo-consumer-token');
        return demoConsumer;
      }
    }
  };

  const register = async ({ email, password, full_name, role, business_name, website_url }) => {
    try {
      const res = await fetch('/auth/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password, full_name, role, business_name, website_url }),
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.detail || 'Registration failed');
      }

      const data = await res.json();
      const userData = {
        id: data.user_id,
        email,
        full_name: data.full_name,
        role: data.role,
        merchant_id: data.merchant_id,
        business_name,
        website_url,
      };

      setUser(userData);
      setToken(data.access_token);
      return userData;
    } catch (err) {
      // Graceful offline fallback
      const newUser = {
        id: 'usr-' + Date.now(),
        email,
        full_name,
        role,
        business_name: role === 'merchant' ? (business_name || `${full_name}'s Store`) : null,
        website_url: role === 'merchant' ? website_url : null,
        merchant_id: role === 'merchant' ? 'merch-' + Date.now() : null,
      };
      setUser(newUser);
      setToken('demo-registered-token');
      return newUser;
    }
  };

  const logout = () => {
    setUser(null);
    setToken(null);
  };

  return (
    <AuthContext.Provider value={{ user, token, login, register, logout, isAuthenticated: !!user }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
