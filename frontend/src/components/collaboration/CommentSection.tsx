// File: src/components/collaboration/CommentSection.tsx
import { useState, useEffect, FormEvent } from 'react'
import { api } from '../../services/api'
import { Comment } from '../../types'
import { useAuth } from '../../hooks/useAuth'
import { useSocket } from '../../hooks/useSocket'
import Button from '../ui/Button'
import LoadingSpinner from '../ui/LoadingSpinner'
import {
  ChatBubbleBottomCenterTextIcon,
  PaperAirplaneIcon,
  TrashIcon,
} from '@heroicons/react/24/outline'

type CommentSectionProps = {
  targetId: string
  targetType: 'project' | 'scene' | 'object'
}

const CommentSection = ({ targetId, targetType }: CommentSectionProps) => {
  const [comments, setComments] = useState<Comment[]>([])
  const [newComment, setNewComment] = useState('')
  const [isLoading, setIsLoading] = useState(true)
  const [isSubmitting, setIsSubmitting] = useState(false)
  const { user } = useAuth()
  const { socket, isConnected } = useSocket()
  
  // Load comments
  useEffect(() => {
    const loadComments = async () => {
      try {
        setIsLoading(true)
        const response = await api.get(`/api/collaboration/comments?targetId=${targetId}&targetType=${targetType}`)
        setComments(response.data)
      } catch (error) {
        console.error('Failed to load comments', error)
      } finally {
        setIsLoading(false)
      }
    }
    
    loadComments()
  }, [targetId, targetType])
  
  // Set up socket for real-time comments
  useEffect(() => {
    if (!socket || !isConnected) return
    
    socket.on('new_comment', (comment: Comment) => {
      if (comment.targetId === targetId) {
        setComments(prevComments => [comment, ...prevComments])
      }
    })
    
    socket.on('delete_comment', (commentId: string) => {
      setComments(prevComments => prevComments.filter(c => c.id !== commentId))
    })
    
    return () => {
      socket.off('new_comment')
      socket.off('delete_comment')
    }
  }, [socket, isConnected, targetId])
  
  const handleSubmitComment = async (e: FormEvent) => {
    e.preventDefault()
    
    if (!newComment.trim() || !user) return
    
    try {
      setIsSubmitting(true)
      
      const response = await api.post('/api/collaboration/comments', {
        targetId,
        targetType,
        content: newComment.trim(),
      })
      
      // Add to local state if socket doesn't update it
      setComments(prevComments => [response.data, ...prevComments])
      setNewComment('')
    } catch (error) {
      console.error('Failed to post comment', error)
    } finally {
      setIsSubmitting(false)
    }
  }
  
  const handleDeleteComment = async (commentId: string) => {
    try {
      await api.delete(`/api/collaboration/comments/${commentId}`)
      
      // Remove from local state if socket doesn't update it
      setComments(prevComments => prevComments.filter(c => c.id !== commentId))
    } catch (error) {
      console.error('Failed to delete comment', error)
    }
  }
  
  const formatDate = (date: string) => {
    const commentDate = new Date(date)
    const now = new Date()
    const diffMs = now.getTime() - commentDate.getTime()
    const diffMins = Math.round(diffMs / 60000)
    const diffHours = Math.round(diffMs / 3600000)
    const diffDays = Math.round(diffMs / 86400000)
    
    if (diffMins < 1) return 'just now'
    if (diffMins < 60) return `${diffMins} ${diffMins === 1 ? 'minute' : 'minutes'} ago`
    if (diffHours < 24) return `${diffHours} ${diffHours === 1 ? 'hour' : 'hours'} ago`
    if (diffDays < 7) return `${diffDays} ${diffDays === 1 ? 'day' : 'days'} ago`
    
    return commentDate.toLocaleDateString()
  }
  
  if (isLoading) {
    return (
      <div className="flex justify-center items-center py-8">
        <LoadingSpinner size="lg" />
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      {/* Comment form */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Add Comment</h3>
        
        <form onSubmit={handleSubmitComment}>
          <textarea
            value={newComment}
            onChange={(e) => setNewComment(e.target.value)}
            className="input-standard min-h-[100px]"
            placeholder="Add your comments, suggestions, or questions..."
            required
          />
          
          <div className="flex justify-end mt-4">
            <Button
              type="submit"
              disabled={!newComment.trim() || isSubmitting}
              isLoading={isSubmitting}
            >
              <PaperAirplaneIcon className="h-5 w-5 mr-1" />
              Post Comment
            </Button>
          </div>
        </form>
      </div>
      
      {/* Comments list */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Comments</h3>
        
        {comments.length > 0 ? (
          <div className="space-y-6 divide-y divide-gray-200">
            {comments.map((comment) => (
              <div key={comment.id} className="pt-6 first:pt-0">
                <div className="flex justify-between">
                  <div className="flex items-center">
                    <div className="h-8 w-8 rounded-full bg-indigo-600 flex items-center justify-center">
                      <span className="text-white font-medium">
                        {comment.username[0].toUpperCase()}
                      </span>
                    </div>
                    <div className="ml-3">
                      <p className="text-sm font-medium text-gray-900">{comment.username}</p>
                      <p className="text-xs text-gray-500">{formatDate(comment.createdAt)}</p>
                    </div>
                  </div>
                  
                  {user?.id === comment.userId && (
                    <button
                      onClick={() => handleDeleteComment(comment.id)}
                      className="text-gray-400 hover:text-red-500"
                    >
                      <TrashIcon className="h-5 w-5" />
                    </button>
                  )}
                </div>
                <div className="mt-2 text-sm text-gray-700 whitespace-pre-wrap">
                  {comment.content}
                </div>
              </div>
            ))}
          </div>
        ) : (
          <div className="text-center py-8 border border-dashed border-gray-300 rounded-md">
            <ChatBubbleBottomCenterTextIcon className="h-10 w-10 text-gray-400 mx-auto" />
            <h3 className="mt-2 text-sm font-medium text-gray-900">No comments yet</h3>
            <p className="mt-1 text-sm text-gray-500">Be the first to add a comment.</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default CommentSection
