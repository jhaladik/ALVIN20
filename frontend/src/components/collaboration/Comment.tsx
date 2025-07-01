// src/components/collaboration/Comment.tsx
import React, { useState } from 'react';
import { format } from 'date-fns';
import { 
  EllipsisHorizontalIcon, 
  PencilIcon, 
  TrashIcon, 
  CheckCircleIcon,
  FlagIcon,
  ChatBubbleLeftIcon
} from '@heroicons/react/24/outline';
import { CheckCircleIcon as CheckCircleSolidIcon } from '@heroicons/react/24/solid';
import { Comment as CommentType } from '../../types/collaboration';
import { useAuth } from '../../context/AuthContext';
import CommentForm from './CommentForm';
import Avatar from '../ui/Avatar';

interface CommentProps {
  comment: CommentType;
  onUpdate: (id: string, content: string) => Promise<void>;
  onDelete: (id: string) => Promise<void>;
  onReply: (parentId: string, content: string) => Promise<void>;
  onResolve: (id: string, isResolved: boolean) => Promise<void>;
  depth?: number;
}

const Comment: React.FC<CommentProps> = ({
  comment,
  onUpdate,
  onDelete,
  onReply,
  onResolve,
  depth = 0,
}) => {
  const { user } = useAuth();
  const [isEditing, setIsEditing] = useState(false);
  const [isReplying, setIsReplying] = useState(false);
  const [showActions, setShowActions] = useState(false);
  const maxDepth = 3; // Maximum nesting level for replies
  
  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return format(date, 'MMM d, yyyy h:mm a');
  };
  
  const handleEdit = () => {
    setIsEditing(true);
    setShowActions(false);
  };
  
  const handleDelete = async () => {
    if (window.confirm('Are you sure you want to delete this comment?')) {
      await onDelete(comment.id);
    }
    setShowActions(false);
  };
  
  const handleUpdate = async (content: string) => {
    await onUpdate(comment.id, content);
    setIsEditing(false);
  };
  
  const handleReply = async (content: string) => {
    await onReply(comment.id, content);
    setIsReplying(false);
  };
  
  const handleResolve = async () => {
    await onResolve(comment.id, !comment.isResolved);
  };
  
  const canModify = user?.id === comment.userId;
  
  // Calculate indentation based on depth
  const indentationClass = depth > 0 ? `ml-${Math.min(depth, maxDepth) * 6}` : '';
  
  return (
    <div className={`mb-4 ${indentationClass}`}>
      <div 
        className={`p-3 rounded-lg ${comment.isResolved ? 'bg-green-50 border border-green-100' : 'bg-white border border-gray-200'}`}
      >
        {/* Comment header */}
        <div className="flex justify-between items-center mb-2">
          <div className="flex items-center">
            <Avatar 
              username={comment.username}
              src={comment.avatar}
              size="sm"
              className="mr-2"
            />
            <div>
              <span className="font-medium text-gray-900">{comment.username}</span>
              <span className="text-xs text-gray-500 ml-2">
                {formatDate(comment.updatedAt)}
                {comment.isEdited && <span className="ml-1">(edited)</span>}
              </span>
            </div>
          </div>
          
          <div className="flex items-center">
            {/* Resolved indicator/button */}
            <button
              onClick={handleResolve}
              className={`mr-2 p-1 rounded-full ${comment.isResolved ? 'text-green-600 hover:text-green-800' : 'text-gray-400 hover:text-gray-600'}`}
              title={comment.isResolved ? 'Mark as unresolved' : 'Mark as resolved'}
            >
              {comment.isResolved ? (
                <CheckCircleSolidIcon className="h-5 w-5" />
              ) : (
                <CheckCircleIcon className="h-5 w-5" />
              )}
            </button>
            
            {/* Action menu button */}
            {canModify && (
              <div className="relative">
                <button
                  onClick={() => setShowActions(!showActions)}
                  className="p-1 rounded-full text-gray-400 hover:text-gray-600"
                >
                  <EllipsisHorizontalIcon className="h-5 w-5" />
                </button>
                
                {/* Dropdown menu for actions */}
                {showActions && (
                  <div 
                    className="absolute right-0 mt-2 w-48 bg-white rounded-md shadow-lg border border-gray-200 z-10"
                    onBlur={() => setShowActions(false)}
                  >
                    <button
                      onClick={handleEdit}
                      className="w-full text-left px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 flex items-center"
                    >
                      <PencilIcon className="h-4 w-4 mr-2" />
                      Edit
                    </button>
                    <button
                      onClick={handleDelete}
                      className="w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-gray-100 flex items-center"
                    >
                      <TrashIcon className="h-4 w-4 mr-2" />
                      Delete
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>
        </div>
        
        {/* Comment content */}
        {isEditing ? (
          <CommentForm
            initialValue={comment.content}
            onSubmit={handleUpdate}
            onCancel={() => setIsEditing(false)}
            submitLabel="Update"
          />
        ) : (
          <div className="text-gray-800 whitespace-pre-wrap break-words">
            {comment.content}
          </div>
        )}
        
        {/* Comment footer with actions */}
        <div className="mt-2 flex text-xs text-gray-500">
          {depth < maxDepth && (
            <button
              onClick={() => setIsReplying(!isReplying)}
              className="flex items-center mr-4 hover:text-gray-700"
            >
              <ChatBubbleLeftIcon className="h-4 w-4 mr-1" />
              Reply
            </button>
          )}
          
          <button className="flex items-center hover:text-gray-700">
            <FlagIcon className="h-4 w-4 mr-1" />
            Report
          </button>
        </div>
      </div>
      
      {/* Reply form */}
      {isReplying && (
        <div className="mt-3 ml-6">
          <CommentForm
            onSubmit={handleReply}
            onCancel={() => setIsReplying(false)}
            submitLabel="Reply"
            initialValue=""
          />
        </div>
      )}
      
      {/* Render children comments (replies) */}
      {comment.children && comment.children.length > 0 && (
        <div className="mt-3">
          {comment.children.map((childComment) => (
            <Comment
              key={childComment.id}
              comment={childComment}
              onUpdate={onUpdate}
              onDelete={onDelete}
              onReply={onReply}
              onResolve={onResolve}
              depth={depth + 1}
            />
          ))}
        </div>
      )}
    </div>
  );
};

export default Comment;
