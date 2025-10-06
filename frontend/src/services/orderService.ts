import api from './api';

export const uploadOrders = async (file: File, timezone: string, token: string) => {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('timezone', timezone);

  try {
    const response = await api.post('/orders/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error uploading orders:', error);
  }
};

export const getOrders = async (token: string) => {
  try {
    const response = await api.get('/orders', {
      headers: {
        Authorization: `Bearer ${token}`,
      },
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching orders:', error);
  }
};
