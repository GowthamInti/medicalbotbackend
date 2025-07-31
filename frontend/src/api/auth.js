import api from './axios';

export const authAPI = {
  // Admin login
  adminLogin: async (credentials) => {
    const response = await api.post('/admin/login', credentials);
    return response.data;
  },

  // User login
  userLogin: async (credentials) => {
    const response = await api.post('/admin/user-login', credentials);
    return response.data;
  },

  // Admin logout
  adminLogout: async () => {
    const response = await api.post('/admin/logout');
    return response.data;
  },

  // Get admin info
  getAdminInfo: async () => {
    const response = await api.get('/admin/info');
    return response.data;
  },

  // Change admin credentials
  changeAdminCredentials: async (data) => {
    const response = await api.post('/admin/change-credentials', data);
    return response.data;
  },

  // Get system status
  getSystemStatus: async () => {
    const response = await api.get('/admin/status');
    return response.data;
  },

  // Test ChatGroq connection
  testChat: async (message) => {
    const response = await api.post('/admin/test-chat', { message });
    return response.data;
  },
};