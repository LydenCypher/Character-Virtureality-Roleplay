import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  const backendUrl = process.env.REACT_APP_BACKEND_URL || 'http://localhost:8001';

  useEffect(() => {
    // Check for existing user in localStorage
    const savedUser = localStorage.getItem('user');
    if (savedUser) {
      setUser(JSON.parse(savedUser));
    }
    setLoading(false);
  }, []);

  const login = async (username, email) => {
    try {
      const response = await axios.post(`${backendUrl}/api/users`, {
        username,
        email
      });
      
      const userData = {
        user_id: response.data.user_id,
        username,
        email
      };
      
      setUser(userData);
      localStorage.setItem('user', JSON.stringify(userData));
      return { success: true };
    } catch (error) {
      if (error.response?.status === 400) {
        // User already exists, try to get user data
        try {
          const existingUsers = await axios.get(`${backendUrl}/api/users`);
          const existingUser = existingUsers.data.find(u => u.email === email);
          if (existingUser) {
            const userData = {
              user_id: existingUser.user_id,
              username: existingUser.username,
              email: existingUser.email
            };
            setUser(userData);
            localStorage.setItem('user', JSON.stringify(userData));
            return { success: true };
          }
        } catch (getError) {
          console.error('Error fetching existing user:', getError);
        }
      }
      return { success: false, error: error.response?.data?.detail || 'Login failed' };
    }
  };

  const logout = () => {
    setUser(null);
    localStorage.removeItem('user');
  };

  const value = {
    user,
    login,
    logout,
    loading
  };

  return (
    <AuthContext.Provider value={value}>
      {!loading && children}
    </AuthContext.Provider>
  );
};