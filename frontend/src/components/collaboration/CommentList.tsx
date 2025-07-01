// src/components/collaboration/CommentList.tsx
import React, { useState, useEffect, useMemo } from 'react';
import { 
  FunnelIcon, 
  CheckCircleIcon, 
  ChatBubbleLeftRightIcon 
} from '@heroicons/react/24/outline';
import { Comment as CommentType } from '../../types/collaboration';
import collaborationService from '../../services/collaborationService';
import { useSocketContext } from '../../context/SocketContext';
import Comment from './Comment';
import CommentForm from './CommentForm';
import LoadingSpinner from '../ui/LoadingSpinner';

interface CommentListProps {
  targetId: string;
  targetType: 'scene' | 'project';
}

const CommentList: React.FC<CommentListProps> = ({ targetId, targetType }) => {
  const [comments, setComments] = useState<CommentType[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filter, setFilter] = useState<'all' | 'unresolved'>('all');
  const { socket, isConnected } = useSocketContext();

  // Load comments
  useEffect(() => {
    const loadComments = async () => {
      try {
        setIsLoading(true);
        setError(null);
        
        let fetchedComments: CommentType[];
        if (targetType === 'scene') {
          fetchedComments = await collaborationService.getSceneComments(targetId);
        } else {
          fetchedComments = await collaborationService.getProjectComments(targetId);
        }
        
        setComments(fetchedComments);
      } catch (err) {
        console.error('Failed to load comments', err);
        setError('Failed to load comments. Please try again.');
      } finally {
        setIsLoading(false);
      }
    };
    
    loadComments();
  }, [targetId, targetType]);

  // Socket.io event listeners for real-time updates
  useEffect(() => {
    if (!socket || !isConnected) return;
    
    // Join the room for this target
    socket.emit('join_room', { roomType: targetType, roomId: targetId });
    
    // Listen for new comments
    socket.on('comment_added', (newComment: CommentType) => {
      if (newComment.targetId === targetId && newComment.targetType === targetType) {
        setComments(prevComments => {
          // If it's a reply, find the parent and add it to children
          if (newComment.parentId) {
            return prevComments.map(comment => {
              if (comment.id === newComment.parentId) {
                return {
                  ...comment,
                  children: [...(comment.children || []), newComment]
                };
              }
              return comment;
            });
          }
          // Otherwise, add it to the root comments
          return [...prevComments, newComment];
        });
      }
    });
    
    // Listen for updated comments
    socket.on('comment_updated', (updatedComment: CommentType) => {
      setComments(prevComments => 
        updateCommentInTree(prevComments, updatedComment)
      );
    });
    
    // Listen for deleted comments
    socket.on('comment_deleted', (deletedCommentId: string) => {
      setComments(prevComments => 
        prevComments.filter(comment => comment.id !== deletedCommentId)
      );
    });
    
    return () => {
      // Leave the room when component unmounts
      socket.emit('leave_room', { roomType: targetType, roomId: targetId });
      socket.off('comment_added');
      socket.off('comment_updated');
      socket.off('comment_deleted');
    };
  }, [socket, isConnected, targetId, targetType]);

  // Helper function to update a comment anywhere in the tree
  const updateCommentInTree = (comments: CommentType[], updatedComment: CommentType): CommentType[] => {
    return comments.map(comment => {
      if (comment.id === updatedComment.id) {
        return updatedComment;
      }
      if (comment.children && comment.children.length > 0) {
        return {
          ...comment,
          children: updateCommentInTree(comment.children, updatedComment)
        };
      }
      return comment;
    });
  };

  // Add a new root comment
  const handleAddComment = async (content: string) => {
    try {
      const newComment = await collaborationService.addComment(
        targetId,
        targetType,
        content
      );
      
      if (newComment && !socket) {
        // If no socket connection, update state manually
        setComments(prevComments => [...prevComments, newComment]);
      }
    } catch (err) {
      console.error('Failed to add comment', err);
      setError('Failed to add comment. Please try again.');
    }
  };

  // Update a comment
  const handleUpdateComment = async (commentId: string, content: string) => {
    try {
      const updatedComment = await collaborationService.updateComment(commentId, content);
      
      if (updatedComment && !socket) {
        // If no socket connection, update state manually
        setComments(prevComments => 
          updateCommentInTree(prevComments, updatedComment)
        );
      }
    } catch (err) {
      console.error('Failed to update comment', err);
      setError('Failed to update comment. Please try again.');
    }
  };

  // Delete a comment
  const handleDeleteComment = async (commentId: string) => {
    try {
      const success = await collaborationService.deleteComment(commentId);
      
      if (success && !socket) {
        // If no socket connection, update state manually
        setComments(prevComments => 
          prevComments.filter(comment => comment.id !== commentId)
        );
      }
    } catch (err) {
      console.error('Failed to delete comment', err);
      setError('Failed to delete comment. Please try again.');
    }
  };

  // Add a reply to a comment
  const handleReplyComment = async (parentId: string, content: string) => {
    try {
      const newReply = await collaborationService.addComment(
        targetId,
        targetType,
        content,
        parentId
      );
      
      if (newReply && !socket) {
        // If no socket connection, update state manually
        setComments(prevComments => {
          return prevComments.map(comment => {
            if (comment.id === parentId) {
              return {
                ...comment,
                children: [...(comment.children || []), newReply]
              };
            }
            return comment;
          });
        });
      }
    } catch (err) {
      console.error('Failed to reply to comment', err);
      setError('Failed to reply to comment. Please try again.');
    }
  };

  // Mark a comment as resolved/unresolved
  const handleResolveComment = async (commentId: string, isResolved: boolean) => {
    try {
      const updatedComment = await collaborationService.updateComment(
        commentId,
        // We're only updating the isResolved status, not the content
        // This is a simplification; in reality, you would need an API endpoint specifically for this
        comments.find(c => c.id === commentId)?.content || ''
      );
      
      if (updatedComment && !socket) {
        // If no socket connection, update state manually
        updatedComment.isResolved = isResolved;
        setComments(prevComments => 
          updateCommentInTree(prevComments, updatedComment)
        );
      }
    } catch (err) {
      console.error('Failed to resolve comment', err);
      setError('Failed to update comment status. Please try again.');
    }
  };

  // Organize comments into a tree structure
  const commentTree = useMemo(() => {
    const rootComments = comments.filter(comment => !comment.parentId);
    
    // Apply filtering
    if (filter === 'unresolved') {
      return rootComments.filter(comment => !comment.isResolved);
    }
    
    return rootComments;
  }, [comments, filter]);

  // Calculate stats
  const commentStats = useMemo(() => {
    const total = comments.length;
    const unresolved = comments.filter(comment => !comment.isResolved).length;
    
    return { total, unresolved };
  }, [comments]);

  if (isLoading) {
    return (
      <div className="p-4 flex justify-center">
        <LoadingSpinner size="md" />
      </div>
    );
  }

  return (
    <div className="bg-gray-50 rounded-lg border border-gray-200 overflow-hidden">
      {/* Header */}
      <div className="bg-white p-4 border-b border-gray-200">
        <div className="flex justify-between items-center">
          <h3 className="text-lg font-medium text-gray-900 flex items-center">
            <ChatBubbleLeftRightIcon className="h-5 w-5 mr-2 text-gray-500" />
            Comments 
            <span className="ml-2 text-sm text-gray-500">
              ({commentStats.total})
            </span>
          </h3>
          
          <div className="flex items-center">
            <span className="text-sm text-gray-500 mr-2">
              Show:
            </span>
            <select
              value={filter}
              onChange={(e) => setFilter(e.target.value as 'all' | 'unresolved')}
              className="block rounded-md border-gray-300 shadow-sm text-sm focus:border-indigo-500 focus:ring-indigo-500"
            >
              <option value="all">All</option>
              <option value="unresolved">Unresolved ({commentStats.unresolved})</option>
            </select>
          </div>
        </div>
      </div>
      
      {/* New comment form */}
      <div className="p-4 border-b border-gray-200">
        <CommentForm
          onSubmit={handleAddComment}
          onCancel={() => {}}
          submitLabel="Comment"
          initialValue=""
        />
      </div>
      
      {/* Error message */}
      {error && (
        <div className="p-4 bg-red-50 text-red-800 border-b border-red-200">
          {error}
        </div>
      )}
      
      {/* Comments list */}
      <div className="p-4">
        {commentTree.length > 0 ? (
          <div className="space-y-4">
            {commentTree.map((comment) => (
              <Comment
                key={comment.id}
                comment={comment}
                onUpdate={handleUpdateComment}
                onDelete={handleDeleteComment}
                onReply={handleReplyComment}
                onResolve={handleResolveComment}
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            <ChatBubbleLeftRightIcon className="h-12 w-12 mx-auto text-gray-300 mb-3" />
            <p className="text-lg">No comments yet</p>
            <p className="text-sm mt-1">
              Be the first to add a comment to this {targetType}
            </p>
          </div>
        )}
      </div>
    </div>
  );
};

export default CommentList;
