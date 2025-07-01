// src/services/aiService.ts
import api from './api';
import { AIAnalysis, AIAnalysisRequest, AIAnalysisResponse } from '../types/ai';

/**
 * Service for interacting with AI-related API endpoints
 */
export const aiService = {
  /**
   * Request AI analysis for a specific scene
   */
  analyzeScene: async (
    sceneId: string,
    criticType: string
  ): Promise<AIAnalysisResponse> => {
    try {
      const response = await api.post<AIAnalysisResponse>('/api/ai/analyze-scene', {
        sceneId,
        criticType,
      });
      
      return response.data;
    } catch (error: any) {
      // Handle token insufficiency errors specially
      if (error.response && error.response.status === 402) {
        return {
          success: false,
          error: 'Insufficient tokens to perform this analysis',
          remainingTokens: error.response.data?.remaining_tokens || 0,
        };
      }
      
      // Generic error handling
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to request AI analysis',
      };
    }
  },
  
  /**
   * Request AI analysis for an entire project
   */
  analyzeProject: async (
    projectId: string,
    criticType: string
  ): Promise<AIAnalysisResponse> => {
    try {
      const response = await api.post<AIAnalysisResponse>(
        `/api/projects/${projectId}/critics/${criticType}`
      );
      
      return response.data;
    } catch (error: any) {
      // Handle token insufficiency errors specially
      if (error.response && error.response.status === 402) {
        return {
          success: false,
          error: 'Insufficient tokens to perform this analysis',
          remainingTokens: error.response.data?.remaining_tokens || 0,
        };
      }
      
      return {
        success: false,
        error: error.response?.data?.error || 'Failed to request project analysis',
      };
    }
  },
  
  /**
   * Get all AI analyses for a scene
   */
  getSceneAnalyses: async (sceneId: string): Promise<AIAnalysis[]> => {
    try {
      const response = await api.get<{ analyses: AIAnalysis[] }>(
        `/api/scenes/${sceneId}/analyses`
      );
      return response.data.analyses;
    } catch (error) {
      console.error('Failed to fetch scene analyses', error);
      return [];
    }
  },
  
  /**
   * Get all AI analyses for a project
   */
  getProjectAnalyses: async (projectId: string): Promise<AIAnalysis[]> => {
    try {
      const response = await api.get<{ analyses: AIAnalysis[] }>(
        `/api/projects/${projectId}/analyses`
      );
      return response.data.analyses;
    } catch (error) {
      console.error('Failed to fetch project analyses', error);
      return [];
    }
  },
  
  /**
   * Request AI-generated scene suggestions
   */
  suggestScenes: async (
    projectId: string,
    count: number = 3
  ): Promise<any> => {
    try {
      const response = await api.post(`/api/ai/projects/${projectId}/suggest-scenes`, {
        count,
      });
      return response.data;
    } catch (error) {
      console.error('Failed to request scene suggestions', error);
      throw error;
    }
  },
  
  /**
   * Analyze overall story structure
   */
  analyzeStoryStructure: async (projectId: string): Promise<any> => {
    try {
      const response = await api.post(`/api/ai/projects/${projectId}/analyze-structure`);
      return response.data;
    } catch (error) {
      console.error('Failed to analyze story structure', error);
      throw error;
    }
  }
};

export default aiService;
