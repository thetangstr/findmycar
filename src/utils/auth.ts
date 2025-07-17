import { useState, useEffect, createContext, useContext, ReactNode } from 'react';
import React from 'react';

// Types
export interface User {
  id: string;
  email: string;
  name: string;
  createdAt: string;
}

interface AuthContextType {
  user: User | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<boolean>;
  register: (email: string, password: string, name: string) => Promise<boolean>;
  logout: () => void;
  resetPassword: (email: string) => Promise<boolean>;
  updateUser: (userData: Partial<User>) => Promise<boolean>;
}

// Create context
export const AuthContext = createContext<AuthContextType | undefined>(undefined);

// Auth provider component
export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // Check for existing session on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        // In a real app, this would verify the session with the server
        const storedUser = localStorage.getItem('auth_user');
        if (storedUser) {
          setUser(JSON.parse(storedUser));
        }
      } catch (err) {
        console.error('Authentication error:', err);
        setError('Failed to authenticate');
      } finally {
        setLoading(false);
      }
    };

    checkAuth();
  }, []);

  // Login function
  const login = async (email: string, password: string): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      // In a real app, this would make an API call to authenticate
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call

      // For demo purposes, any email/password combination works
      // In a real app, this would validate credentials against the server
      const mockUser: User = {
        id: '123456',
        email,
        name: email.split('@')[0],
        createdAt: new Date().toISOString()
      };

      setUser(mockUser);
      localStorage.setItem('auth_user', JSON.stringify(mockUser));
      return true;
    } catch (err) {
      console.error('Login error:', err);
      setError('Invalid email or password');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Register function
  const register = async (email: string, password: string, name: string): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      // In a real app, this would make an API call to register
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call

      // For demo purposes, registration always succeeds
      // In a real app, this would create a new user on the server
      const mockUser: User = {
        id: Date.now().toString(),
        email,
        name,
        createdAt: new Date().toISOString()
      };

      setUser(mockUser);
      localStorage.setItem('auth_user', JSON.stringify(mockUser));
      return true;
    } catch (err) {
      console.error('Registration error:', err);
      setError('Failed to register');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Logout function
  const logout = () => {
    setUser(null);
    localStorage.removeItem('auth_user');
  };

  // Update user function
  const updateUser = async (userData: Partial<User>): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      // In a real app, this would make an API call to update user data
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call

      if (user) {
        const updatedUser = { ...user, ...userData };
        setUser(updatedUser);
        localStorage.setItem('auth_user', JSON.stringify(updatedUser));
        return true;
      }
      return false;
    } catch (err) {
      console.error('Update user error:', err);
      setError('Failed to update user information');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // Reset password function
  const resetPassword = async (email: string): Promise<boolean> => {
    setLoading(true);
    setError(null);

    try {
      // In a real app, this would make an API call to reset password
      await new Promise(resolve => setTimeout(resolve, 1000)); // Simulate API call

      // For demo purposes, reset always succeeds
      // In a real app, this would send a reset email
      return true;
    } catch (err) {
      console.error('Password reset error:', err);
      setError('Failed to reset password');
      return false;
    } finally {
      setLoading(false);
    }
  };

  const value = {
    user,
    loading,
    error,
    login,
    register,
    logout,
    resetPassword,
    updateUser
  };

  return React.createElement(AuthContext.Provider, { value }, children);
};

// Custom hook to use auth context
export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
