// src/types/collaboration.ts
// TypeScript interfaces for collaboration-related data structures

export type CollaborationRole = 'owner' | 'editor' | 'commenter' | 'viewer';

export interface Collaborator {
  id: string;
  userId: string;
  username: string;
  email: string;
  role: CollaborationRole;
  avatar?: string;
  joinedAt: string;
  lastActive?: string;
}

export interface Invitation {
  id: string;
  projectId: string;
  projectName: string;
  inviterId: string;
  inviterName: string;
  email: string;
  role: CollaborationRole;
  status: 'pending' | 'accepted' | 'declined' | 'expired';
  createdAt: string;
  expiresAt: string;
}

export interface Comment {
  id: string;
  targetId: string; // sceneId or projectId
  targetType: 'scene' | 'project';
  userId: string;
  username: string;
  avatar?: string;
  content: string;
  parentId?: string;
  createdAt: string;
  updatedAt: string;
  isEdited: boolean;
  isResolved: boolean;
  reactions?: CommentReaction[];
  children?: Comment[];
}

export interface CommentReaction {
  id: string;
  commentId: string;
  userId: string;
  username: string;
  type: string; // e.g., 'like', 'heart', 'thumbsup'
  createdAt: string;
}

export interface CollaborationStatus {
  isCollaborative: boolean;
  role: CollaborationRole;
  collaborators: Collaborator[];
  canInvite: boolean;
  canEditRoles: boolean;
  canRemoveCollaborators: boolean;
}

export interface PresenceUpdate {
  users: {
    id: string;
    username: string;
    avatar?: string;
  }[];
  roomId: string;
  roomType: 'project' | 'scene';
}

export interface TypingStatus {
  userId: string;
  username: string;
  roomId: string;
  roomType: 'project' | 'scene';
  isTyping: boolean;
  timestamp: string;
}

export interface CollaborationUpdate {
  type: 'comment_added' | 'comment_updated' | 'comment_deleted' | 'collaborator_added' | 'collaborator_removed' | 'role_updated';
  data: any;
  timestamp: string;
}

export interface CollaborativeChange {
  userId: string;
  username: string;
  targetId: string;
  targetType: 'scene' | 'project';
  fieldName: string;
  oldValue?: any;
  newValue: any;
  timestamp: string;
}
