// src/components/collaboration/CommentForm.tsx
import React, { useState, useRef, useEffect } from 'react';
import { PaperAirplaneIcon, XMarkIcon } from '@heroicons/react/24/outline';

interface CommentFormProps {
  onSubmit: (content: string) => Promise<void>;
  onCancel: () => void;
  submitLabel: string;
  initialValue: string;
  placeholder?: string;
}

const CommentForm: React.FC<CommentFormProps> = ({
  onSubmit,
  onCancel,
  submitLabel,
  initialValue,
  placeholder = 'Add a comment...',
}) => {
  const [content, setContent] = useState(initialValue);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  useEffect(() => {
    // Focus the textarea and place cursor at the end
    if (textareaRef.current) {
      textareaRef.current.focus();
      textareaRef.current.selectionStart = textareaRef.current.value.length;
    }
  }, []);

  // Auto-resize the textarea as content grows
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [content]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!content.trim()) return;
    
    try {
      setIsSubmitting(true);
      await onSubmit(content);
      setContent('');
    } catch (error) {
      console.error('Failed to submit comment', error);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <form onSubmit={handleSubmit} className="relative">
      <div className="border border-gray-300 rounded-lg overflow-hidden focus-within:border-indigo-500 focus-within:ring-1 focus-within:ring-indigo-500">
        <textarea
          ref={textareaRef}
          value={content}
          onChange={(e) => setContent(e.target.value)}
          placeholder={placeholder}
          rows={1}
          className="block w-full px-3 py-2 resize-none border-0 focus:ring-0 text-sm"
          disabled={isSubmitting}
        />
        
        <div className="flex justify-between items-center bg-gray-50 px-3 py-2 border-t border-gray-200">
          <div className="text-xs text-gray-500">
            <span className={content.length > 0 ? 'text-indigo-600' : ''}>
              {content.length}
            </span> / 1000
          </div>
          
          <div className="flex space-x-2">
            <button
              type="button"
              onClick={onCancel}
              className="inline-flex items-center px-2.5 py-1.5 text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-100 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              disabled={isSubmitting}
            >
              <XMarkIcon className="h-4 w-4 mr-1" />
              Cancel
            </button>
            
            <button
              type="submit"
              className="inline-flex items-center px-2.5 py-1.5 text-xs font-medium rounded text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              disabled={isSubmitting || !content.trim()}
            >
              <PaperAirplaneIcon className="h-4 w-4 mr-1" />
              {submitLabel}
            </button>
          </div>
        </div>
      </div>
    </form>
  );
};

export default CommentForm;
