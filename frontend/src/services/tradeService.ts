import axios from './api';
import type { Trade } from '../types';

export const getTrades = async (token: string): Promise<Trade[]> => {
  const response = await axios.get('/trades', {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return response.data;
};
