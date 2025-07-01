// src/components/collaboration/CollaboratorsList.tsx
import React, { useState, useEffect } from 'react';
import { 
  UserGroupIcon, 
  UserPlusIcon, 
  UserMinusIcon, 
  PencilIcon,
  CheckIcon,
  XMarkIcon
} from '@heroicons/react/24/outline';
import { format } from 'date-fns';
import { Collaborator, CollaborationRole, Invitation } from '../../types/collaboration';
import collaborationService from '../../services/collaborationService';
import { useAuth } from '../../context/AuthContext';
import Avatar from '../ui/Avatar';
import Button from '../ui/Button';
import LoadingSpinner from '../ui/LoadingSpinner';

interface CollaboratorsListProps {
  projectId: string;
}

const CollaboratorsList: React.FC<CollaboratorsListProps> = ({ projectId }) => {
  const { user } = useAuth();
  const [collaborators, setCollaborators] = useState<Collaborator[]>([]);
  const [invitations, setInvitations] = useState<Invitation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [showInviteForm, setShowInviteForm] = useState(false);
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteRole, setInviteRole] = useState<CollaborationRole>('editor');
  const [isSendingInvite, setIsSendingInvite] = useState(false);
  const [editingCollaborator, setEditingCollaborator] = useState<string | null>(null);
  const [editRole, setEditRole] = useState<CollaborationRole>('editor');

  // Get user's role in this project
  const userRole = collaborators.find(c => c.userId === user?.id)?.role || 'viewer';
  const isOwner = userRole === 'owner';
  const canManageCollaborators = isOwner || userRole === 'editor';

  // Load collaborators and invitations
  useEffect(() => {
    const loadCollaborationData = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        const [fetchedCollaborators, fetchedInvitations] = await Promise.all([
          collaborationService.getCollaborators(projectId),
          collaborationService.getInvitations(projectId),
        ]);
        
        setCollaborators(fetchedCollaborators);
        setInvitations(fetchedInvitations);
      } catch (err) {
        console.error('Failed to load collaboration data', err);
        setError('Failed to load collaborators. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadCollaborationData();
  }, [projectId]);

  // Send invitation
  const handleSendInvite = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!inviteEmail.trim()) return;
    
    try {
      setIsSendingInvite(true);
      setError(null);
      
      const newInvitation = await collaborationService.inviteCollaborator(
        projectId,
        inviteEmail,
        inviteRole
      );
      
      if (newInvitation) {
        setInvitations(prev => [...prev, newInvitation]);
        setInviteEmail('');
        setShowInviteForm(false);
      }
    } catch (err) {
      console.error('Failed to send invitation', err);
      setError('Failed to send invitation. Please try again.');
    } finally {
      setIsSendingInvite(false);
    }
  };

  // Update collaborator role
  const handleUpdateRole = async (userId: string, newRole: CollaborationRole) => {
    try {
      setError(null);
      
      const success = await collaborationService.updateCollaboratorRole(
        projectId,
        userId,
        newRole
      );
      
      if (success) {
        setCollaborators(prev => 
          prev.map(c => c.userId === userId ? { ...c, role: newRole } : c)
        );
        setEditingCollaborator(null);
      }
    } catch (err) {
      console.error('Failed to update collaborator role', err);
      setError('Failed to update role. Please try again.');
    }
  };

  // Remove collaborator
  const handleRemoveCollaborator = async (userId: string) => {
    if (!window.confirm('Are you sure you want to remove this collaborator?')) {
      return;
    }
    
    try {
      setError(null);
      
      const success = await collaborationService.removeCollaborator(
        projectId,
        userId
      );
      
      if (success) {
        setCollaborators(prev => 
          prev.filter(c => c.userId !== userId)
        );
      }
    } catch (err) {
      console.error('Failed to remove collaborator', err);
      setError('Failed to remove collaborator. Please try again.');
    }
  };

  // Cancel invitation
  const handleCancelInvitation = async (invitationId: string) => {
    if (!window.confirm('Are you sure you want to cancel this invitation?')) {
      return;
    }
    
    try {
      setError(null);
      
      // This is a simplified approach; in reality, you would need an API endpoint specifically for this
      const success = await collaborationService.declineInvitation(invitationId);
      
      if (success) {
        setInvitations(prev => 
          prev.filter(inv => inv.id !== invitationId)
        );
      }
    } catch (err) {
      console.error('Failed to cancel invitation', err);
      setError('Failed to cancel invitation. Please try again.');
    }
  };

  // Format date
  const formatDate = (dateString: string) => {
    return format(new Date(dateString), 'MMM d, yyyy');
  };

  // Get role badge class
  const getRoleBadgeClass = (role: CollaborationRole) => {
    switch (role) {
      case 'owner':
        return 'bg-purple-100 text-purple-800';
      case 'editor':
        return 'bg-blue-100 text-blue-800';
      case 'commenter':
        return 'bg-green-100 text-green-800';
      case 'viewer':
        return 'bg-gray-100 text-gray-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  if (isLoading) {
    return (
      <div className="p-4 flex justify-center">
        <LoadingSpinner size="md" />
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-gray-50 p-4 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <UserGroupIcon className="h-5 w-5 mr-2 text-gray-500" />
            Collaborators 
            <span className="ml-2 text-sm text-gray-500">
              ({collaborators.length})
            </span>
          </h3>
          
          {canManageCollaborators && (
            <Button 
              variant="secondary"
              size="sm"
              onClick={() => setShowInviteForm(!showInviteForm)}
            >
              <UserPlusIcon className="h-4 w-4 mr-1" />
              Invite
            </Button>
          )}
        </div>
      </div>
      
      {/* Invite form */}
      {showInviteForm && (
        <div className="p-4 bg-indigo-50 border-b border-indigo-100">
          <form onSubmit={handleSendInvite}>
            <div className="sm:flex sm:items-start sm:justify-between">
              <div className="w-full sm:max-w-xs mb-2 sm:mb-0 sm:mr-4">
                <label htmlFor="email" className="sr-only">
                  Email address
                </label>
                <input
                  type="email"
                  id="email"
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="Email address"
                  required
                  className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                  disabled={isSendingInvite}
                />
              </div>
              
              <div className="flex items-center">
                <div className="w-36 mr-2">
                  <select
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value as CollaborationRole)}
                    className="block w-full rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 sm:text-sm"
                    disabled={isSendingInvite}
                  >
                    {isOwner && <option value="editor">Editor</option>}
                    <option value="commenter">Commenter</option>
                    <option value="viewer">Viewer</option>
                  </select>
                </div>
                
                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  disabled={isSendingInvite || !inviteEmail.trim()}
                >
                  {isSendingInvite ? (
                    <LoadingSpinner size="sm" />
                  ) : (
                    <>
                      <UserPlusIcon className="h-4 w-4 mr-1" />
                      Send Invite
                    </>
                  )}
                </Button>
              </div>
            </div>
          </form>
          
          <div className="mt-2 text-xs text-indigo-700">
            <p>
              <strong>Editor:</strong> Can edit scenes and invite others
            </p>
            <p>
              <strong>Commenter:</strong> Can add comments but not edit content
            </p>
            <p>
              <strong>Viewer:</strong> Can only view content
            </p>
          </div>
        </div>
      )}
      
      {/* Error message */}
      {error && (
        <div className="p-4 bg-red-50 text-red-800 border-b border-red-200">
          {error}
        </div>
      )}
      
      {/* Collaborators list */}
      <div className="divide-y divide-gray-200">
        {collaborators.map((collaborator) => (
          <div key={collaborator.userId} className="p-4 flex items-center justify-between">
            <div className="flex items-center">
              <Avatar 
                username={collaborator.username}
                src={collaborator.avatar}
                size="md"
                className="mr-3"
              />
              <div>
                <p className="font-medium text-gray-900">
                  {collaborator.username}
                  {collaborator.userId === user?.id && ' (You)'}
                </p>
                <p className="text-sm text-gray-500">{collaborator.email}</p>
                <div className="flex items-center mt-1">
                  <span
                    className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeClass(
                      collaborator.role
                    )}`}
                  >
                    {collaborator.role}
                  </span>
                  <span className="text-xs text-gray-500 ml-2">
                    Joined {formatDate(collaborator.joinedAt)}
                  </span>
                </div>
              </div>
            </div>
            
            {/* Actions */}
            {isOwner && collaborator.userId !== user?.id && (
              <div className="flex items-center">
                {editingCollaborator === collaborator.userId ? (
                  <div className="flex items-center">
                    <select
                      value={editRole}
                      onChange={(e) => setEditRole(e.target.value as CollaborationRole)}
                      className="block rounded-md border-gray-300 shadow-sm focus:border-indigo-500 focus:ring-indigo-500 text-sm mr-2"
                    >
                      <option value="editor">Editor</option>
                      <option value="commenter">Commenter</option>
                      <option value="viewer">Viewer</option>
                    </select>
                    
                    <button
                      onClick={() => handleUpdateRole(collaborator.userId, editRole)}
                      className="p-1.5 rounded-full text-green-600 hover:bg-green-50"
                      title="Save"
                    >
                      <CheckIcon className="h-5 w-5" />
                    </button>
                    
                    <button
                      onClick={() => setEditingCollaborator(null)}
                      className="p-1.5 rounded-full text-gray-500 hover:bg-gray-50"
                      title="Cancel"
                    >
                      <XMarkIcon className="h-5 w-5" />
                    </button>
                  </div>
                ) : (
                  <>
                    <button
                      onClick={() => {
                        setEditingCollaborator(collaborator.userId);
                        setEditRole(collaborator.role);
                      }}
                      className="p-1.5 rounded-full text-gray-500 hover:bg-gray-50 mr-1"
                      title="Edit role"
                    >
                      <PencilIcon className="h-5 w-5" />
                    </button>
                    
                    <button
                      onClick={() => handleRemoveCollaborator(collaborator.userId)}
                      className="p-1.5 rounded-full text-red-500 hover:bg-red-50"
                      title="Remove collaborator"
                    >
                      <UserMinusIcon className="h-5 w-5" />
                    </button>
                  </>
                )}
              </div>
            )}
          </div>
        ))}
      </div>
      
      {/* Pending invitations */}
      {invitations.length > 0 && (
        <div className="border-t border-gray-200">
          <div className="p-4 bg-gray-50">
            <h4 className="text-sm font-medium text-gray-700">
              Pending Invitations ({invitations.length})
            </h4>
          </div>
          
          <div className="divide-y divide-gray-200">
            {invitations.map((invitation) => (
              <div key={invitation.id} className="p-4 flex items-center justify-between">
                <div>
                  <p className="font-medium text-gray-900">{invitation.email}</p>
                  <div className="flex items-center mt-1">
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${getRoleBadgeClass(
                        invitation.role
                      )}`}
                    >
                      {invitation.role}
                    </span>
                    <span className="text-xs text-gray-500 ml-2">
                      Invited on {formatDate(invitation.createdAt)}
                    </span>
                    <span className="text-xs text-amber-600 ml-2">
                      Expires on {formatDate(invitation.expiresAt)}
                    </span>
                  </div>
                </div>
                
                {/* Actions */}
                {canManageCollaborators && (
                  <button
                    onClick={() => handleCancelInvitation(invitation.id)}
                    className="p-1.5 rounded-full text-red-500 hover:bg-red-50"
                    title="Cancel invitation"
                  >
                    <XMarkIcon className="h-5 w-5" />
                  </button>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
      
      {/* Empty state */}
      {collaborators.length === 0 && (
        <div className="p-8 text-center">
          <UserGroupIcon className="h-12 w-12 mx-auto text-gray-300 mb-3" />
          <p className="text-lg text-gray-900">No collaborators yet</p>
          <p className="text-sm text-gray-500 mt-1">
            Invite team members to collaborate on this project
          </p>
        </div>
      )}
    </div>
  );
};

export default CollaboratorsList;
