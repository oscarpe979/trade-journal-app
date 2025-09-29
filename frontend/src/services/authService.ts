import api from './api';
import type { UserLogin, UserCreate } from '../types';

export const login = async (credentials: UserLogin) => {
  const response = await api.post('/login/access-token', new URLSearchParams(credentials), {
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
