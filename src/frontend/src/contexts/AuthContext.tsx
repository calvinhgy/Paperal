import React, { createContext, useState, useEffect, useContext } from 'react';
import axios from 'axios';

interface User {
  id: string;
  email: string;
  name: string;
  organization?: string;
  role: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  loading: boolean;
  error: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, name: string, password: string, organization?: string) => Promise<void>;
  logout: () => void;
  clearError: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(localStorage.getItem('token'));
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  // 设置axios默认头部
  useEffect(() => {
    if (token) {
      axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;
    } else {
      delete axios.defaults.headers.common['Authorization'];
    }
  }, [token]);

  // 加载用户信息
  useEffect(() => {
    const loadUser = async () => {
      if (!token) {
        setLoading(false);
        return;
      }

      try {
        const response = await axios.get('/api/users/me');
        if (response.data.success) {
          setUser(response.data.data);
        } else {
          localStorage.removeItem('token');
          setToken(null);
          setError('会话已过期，请重新登录');
        }
      } catch (err) {
        localStorage.removeItem('token');
        setToken(null);
        setError('加载用户信息失败');
      } finally {
        setLoading(false);
      }
    };

    loadUser();
  }, [token]);

  // 登录
  const login = async (email: string, password: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/auth/token', {
        username: email,
        password: password
      });

      if (response.data.success) {
        const { access_token } = response.data.data;
        localStorage.setItem('token', access_token);
        setToken(access_token);
      } else {
        setError(response.data.error?.message || '登录失败');
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || '登录失败');
    } finally {
      setLoading(false);
    }
  };

  // 注册
  const register = async (email: string, name: string, password: string, organization?: string) => {
    setLoading(true);
    setError(null);

    try {
      const response = await axios.post('/api/auth/register', {
        email,
        name,
        password,
        organization
      });

      if (response.data.success) {
        const { access_token, user } = response.data.data;
        localStorage.setItem('token', access_token);
        setToken(access_token);
        setUser(user);
      } else {
        setError(response.data.error?.message || '注册失败');
      }
    } catch (err: any) {
      setError(err.response?.data?.error?.message || '注册失败');
    } finally {
      setLoading(false);
    }
  };

  // 登出
  const logout = () => {
    localStorage.removeItem('token');
    setToken(null);
    setUser(null);
  };

  // 清除错误
  const clearError = () => {
    setError(null);
  };

  const value = {
    user,
    token,
    loading,
    error,
    login,
    register,
    logout,
    clearError
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};