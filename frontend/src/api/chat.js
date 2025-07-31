import api from './axios';

export const chatAPI = {
  // Send message to chat
  sendMessage: async (sessionId, message) => {
    const response = await api.post('/chat/', {
      session_id: sessionId,
      message: message,
    });
    return response.data;
  },

  // Clear chat session
  clearSession: async (sessionId) => {
    const response = await api.delete(`/chat/sessions/${sessionId}`);
    return response.data;
  },

  // Get memory statistics (admin only)
  getMemoryStats: async () => {
    const response = await api.get('/chat/memory/stats');
    return response.data;
  },

  // Get health status
  getHealth: async () => {
    const response = await api.get('/health');
    return response.data;
  },

  // Get LLM provider info
  getLLMProvider: async () => {
    const response = await api.get('/llm/provider');
    return response.data;
  },
};