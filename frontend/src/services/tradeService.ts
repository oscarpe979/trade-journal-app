import api from './api';

export const uploadTrades = async (file: File, token: string) => {
  const formData = new FormData();
  formData.append('file', file);

  try {
    const response = await api.post('/trades/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading trades:', error);
  }
};

export const getTrades = async (token: string) => {
  try {
    const response = await api.get('/trades', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching trades:', error);
  }
};
