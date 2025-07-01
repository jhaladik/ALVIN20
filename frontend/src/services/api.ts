// File: src/services/api.ts
import axios from 'axios';

// Create an axios instance with common config
export const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:5000',
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Important for cookies/session authentication
});

// Modify your error interceptor in api.ts
api.interceptors.response.use(
  (response) => response,
  (error) => {
    // Only redirect for 401 errors that aren't from the /api/auth/me endpoint
    if (
      error.response && 
      error.response.status === 401 && 
      !error.config.url.includes('/api/auth/me')
    ) {
      // Redirect to login if session expired
      window.location.href = '/login';
    }
    
    return Promise.reject(error);
  }
);

// API service functions for more specific operations
export const authService = {
  login: async (email: string, password: string) => {
    return api.post('/api/auth/login', { email, password });
  },
  
  register: async (username: string, email: string, password: string) => {
    return api.post('/api/auth/register', { username, email, password });
  },
  
  getCurrentUser: async () => {
    return api.get('/api/auth/me');
  },
  
  logout: async () => {
    return api.post('/api/auth/logout');
  },
};

export const projectService = {
  getProjects: async (params = {}) => {
    return api.get('/api/projects', { params });
  },
  
  getProject: async (id: string) => {
    return api.get(`/api/projects/${id}`);
  },
  
  createProject: async (data: any) => {
    return api.post('/api/projects', data);
  },
  
  updateProject: async (id: string, data: any) => {
    return api.put(`/api/projects/${id}`, data);
  },
  
  deleteProject: async (id: string) => {
    return api.delete(`/api/projects/${id}`);
  },
};

export const sceneService = {
  getScenes: async (projectId: string, params = {}) => {
    return api.get(`/api/projects/${projectId}/scenes`, { params });
  },
  
  getScene: async (projectId: string, sceneId: string) => {
    return api.get(`/api/projects/${projectId}/scenes/${sceneId}`);
  },
  
  createScene: async (projectId: string, data: any) => {
    return api.post(`/api/projects/${projectId}/scenes`, data);
  },
  
  updateScene: async (projectId: string, sceneId: string, data: any) => {
    return api.put(`/api/projects/${projectId}/scenes/${sceneId}`, data);
  },
  
  deleteScene: async (projectId: string, sceneId: string) => {
    return api.delete(`/api/projects/${projectId}/scenes/${sceneId}`);
  },
  
  reorderScenes: async (projectId: string, sceneOrder: { id: string, order: number }[]) => {
    return api.post(`/api/projects/${projectId}/scenes/reorder`, { sceneOrder });
  },
};

export const objectService = {
  getObjects: async (projectId: string, type?: string) => {
    return api.get(`/api/projects/${projectId}/objects`, { params: { type } });
  },
  
  getObject: async (projectId: string, objectId: string) => {
    return api.get(`/api/projects/${projectId}/objects/${objectId}`);
  },
  
  createObject: async (projectId: string, data: any) => {
    return api.post(`/api/projects/${projectId}/objects`, data);
  },
  
  updateObject: async (projectId: string, objectId: string, data: any) => {
    return api.put(`/api/projects/${projectId}/objects/${objectId}`, data);
  },
  
  deleteObject: async (projectId: string, objectId: string) => {
    return api.delete(`/api/projects/${projectId}/objects/${objectId}`);
  },
  
  getRelationships: async (projectId: string) => {
    return api.get(`/api/projects/${projectId}/relationships`);
  },
  
  updateRelationship: async (projectId: string, data: any) => {
    return api.post(`/api/projects/${projectId}/relationships`, data);
  },
};

export const aiService = {
  analyzeIdea: async (idea: string, storyIntent?: string) => {
    return api.post('/api/ai/analyze-idea', { idea, story_intent: storyIntent });
  },
  
  createProjectFromIdea: async (idea: string, analysisId?: string) => {
    return api.post('/api/ai/create-project-from-idea', { idea, analysis_id: analysisId });
  },
  
  analyzeScene: async (projectId: string, sceneId: string, criticType: string) => {
    return api.post(`/api/ai/projects/${projectId}/scenes/${sceneId}/analyze`, { critic_type: criticType });
  },
  
  analyzeStructure: async (projectId: string) => {
    return api.post(`/api/ai/projects/${projectId}/analyze-structure`);
  },
  
  suggestScenes: async (projectId: string) => {
    return api.post(`/api/ai/projects/${projectId}/suggest-scenes`);
  },
  
  generateStory: async (projectId: string, options?: any) => {
    return api.post(`/api/ai/projects/${projectId}/generate-story`, options);
  },
  
  getTasks: async (limit = 5) => {
    return api.get('/api/ai/tasks', { params: { limit } });
  },
};

export const collaborationService = {
  getCollaborators: async (projectId: string) => {
    return api.get(`/api/collaboration/projects/${projectId}/collaborators`);
  },
  
  inviteCollaborator: async (projectId: string, email: string, permission: string) => {
    return api.post(`/api/collaboration/projects/${projectId}/invite`, { email, permission });
  },
  
  removeCollaborator: async (projectId: string, userId: string) => {
    return api.delete(`/api/collaboration/projects/${projectId}/collaborators/${userId}`);
  },
  
  getComments: async (projectId: string, targetId?: string, targetType?: string) => {
    return api.get(`/api/collaboration/projects/${projectId}/comments`, {
      params: { target_id: targetId, target_type: targetType }
    });
  },
  
  addComment: async (projectId: string, targetId: string, targetType: string, content: string) => {
    return api.post(`/api/collaboration/projects/${projectId}/comments`, {
      target_id: targetId,
      target_type: targetType,
      content
    });
  },
  
  deleteComment: async (projectId: string, commentId: string) => {
    return api.delete(`/api/collaboration/projects/${projectId}/comments/${commentId}`);
  },
};

export const billingService = {
  getPlans: async () => {
    return api.get('/api/billing/plans');
  },
  
  getCurrentSubscription: async () => {
    return api.get('/api/billing/subscription');
  },
  
  subscribe: async (planId: string) => {
    return api.post('/api/billing/subscribe', { plan_id: planId });
  },
  
  cancelSubscription: async () => {
    return api.post('/api/billing/cancel');
  },
  
  buyTokens: async (amount: number) => {
    return api.post('/api/billing/buy-tokens', { amount });
  },
  
  getTokenUsage: async (period = 'month') => {
    return api.get('/api/billing/token-usage', { params: { period } });
  },
};

export default {
  auth: authService,
  projects: projectService,
  scenes: sceneService,
  objects: objectService,
  ai: aiService,
  collaboration: collaborationService,
  billing: billingService,
};