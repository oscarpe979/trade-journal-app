import axios from 'axios';
import eventBus from './eventBus';

const api = axios.create({
  baseURL: 'http://localhost:8000/api/v1',
});

// Logout Interceptor
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      eventBus.dispatch('logout');
    }
    return Promise.reject(error);
  }
);

// Response error interceptor
api.interceptors.response.use((response) => response, (error) => {
    // Check if the error is from Axios and has the structure we expect
    if (axios.isAxiosError(error) && error.response?.data?.detail) {      
      return Promise.reject(new Error(error.response.data.detail));
    }
    return Promise.reject(error);
  }
);

export default api;
