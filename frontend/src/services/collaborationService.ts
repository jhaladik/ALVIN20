// src/services/collaborationService.ts
import api from './api';
import { Comment, Invitation, CollaborationRole } from '../types/collaboration';

/**
 * Service for interacting with collaboration-related API endpoints
 */
export const collaborationService = {
  /**
   * Get all comments for a scene
   */
  getSceneComments: async (sceneId: string): Promise<Comment[]> => {
    try {
      const response = await api.get(`/api/collaboration/comments?targetId=${sceneId}&targetType=scene`);
      return response.data.comments;
    } catch (error) {
      console.error('Failed to fetch scene comments', error);
      return [];
    }
  },

  /**
   * Get all comments for a project
   */
  getProjectComments: async (projectId: string): Promise<Comment[]> => {
    try {
      const response = await api.get(`/api/collaboration/comments?targetId=${projectId}&targetType=project`);
      return response.data.comments;
    } catch (error) {
      console.error('Failed to fetch project comments', error);
      return [];
    }
  },

  /**
   * Add a comment to a scene or project
   */
  addComment: async (
    targetId: string,
    targetType: 'scene' | 'project',
    content: string,
    parentId?: string
  ): Promise<Comment | null> => {
    try {
      const response = await api.post('/api/collaboration/comments', {
        targetId,
        targetType,
        content,
        parentId,
      });
      return response.data.comment;
    } catch (error) {
      console.error('Failed to add comment', error);
      return null;
    }
  },

  /**
   * Update a comment
   */
  updateComment: async (
    commentId: string,
    content: string
  ): Promise<Comment | null> => {
    try {
      const response = await api.put(`/api/collaboration/comments/${commentId}`, {
        content,
      });
      return response.data.comment;
    } catch (error) {
      console.error('Failed to update comment', error);
      return null;
    }
  },

  /**
   * Delete a comment
   */
  deleteComment: async (commentId: string): Promise<boolean> => {
    try {
      await api.delete(`/api/collaboration/comments/${commentId}`);
      return true;
    } catch (error) {
      console.error('Failed to delete comment', error);
      return false;
    }
  },

  /**
   * Get all collaborators for a project
   */
  getCollaborators: async (projectId: string): Promise<any[]> => {
    try {
      const response = await api.get(`/api/collaboration/projects/${projectId}/collaborators`);
      return response.data.collaborators;
    } catch (error) {
      console.error('Failed to fetch collaborators', error);
      return [];
    }
  },

  /**
   * Get all invitations for a project
   */
  getInvitations: async (projectId: string): Promise<Invitation[]> => {
    try {
      const response = await api.get(`/api/collaboration/projects/${projectId}/invitations`);
      return response.data.invitations;
    } catch (error) {
      console.error('Failed to fetch invitations', error);
      return [];
    }
  },

  /**
   * Invite a user to collaborate on a project
   */
  inviteCollaborator: async (
    projectId: string,
    email: string,
    role: CollaborationRole
  ): Promise<Invitation | null> => {
    try {
      const response = await api.post(`/api/collaboration/projects/${projectId}/invitations`, {
        email,
        role,
      });
      return response.data.invitation;
    } catch (error) {
      console.error('Failed to invite collaborator', error);
      return null;
    }
  },

  /**
   * Accept an invitation to collaborate
   */
  acceptInvitation: async (invitationId: string): Promise<boolean> => {
    try {
      await api.post(`/api/collaboration/invitations/${invitationId}/accept`);
      return true;
    } catch (error) {
      console.error('Failed to accept invitation', error);
      return false;
    }
  },

  /**
   * Decline an invitation to collaborate
   */
  declineInvitation: async (invitationId: string): Promise<boolean> => {
    try {
      await api.post(`/api/collaboration/invitations/${invitationId}/decline`);
      return true;
    } catch (error) {
      console.error('Failed to decline invitation', error);
      return false;
    }
  },

  /**
   * Remove a collaborator from a project
   */
  removeCollaborator: async (
    projectId: string,
    userId: string
  ): Promise<boolean> => {
    try {
      await api.delete(`/api/collaboration/projects/${projectId}/collaborators/${userId}`);
      return true;
    } catch (error) {
      console.error('Failed to remove collaborator', error);
      return false;
    }
  },

  /**
   * Update a collaborator's role in a project
   */
  updateCollaboratorRole: async (
    projectId: string,
    userId: string,
    role: CollaborationRole
  ): Promise<boolean> => {
    try {
      await api.put(`/api/collaboration/projects/${projectId}/collaborators/${userId}`, {
        role,
      });
      return true;
    } catch (error) {
      console.error('Failed to update collaborator role', error);
      return false;
    }
  },
};

export default collaborationService;
