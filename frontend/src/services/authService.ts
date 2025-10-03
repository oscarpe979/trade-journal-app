import api from './api';
import type { UserLogin, UserCreate } from '../types';

export const login = async (credentials: UserLogin) => {

  const params = new URLSearchParams();
  Object.entries(credentials).forEach(([key, value]) => {
    params.append(key, String(value));
  });
  
  const response = await api.post('/login/access-token', params, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  });
  return response.data;
};

export const signup = async (credentials: UserCreate) => {
  const response = await api.post('/users', credentials);
  return response.data;
};
