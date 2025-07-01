// File: src/components/projects/CreateProjectModal.tsx
import { useState, FormEvent } from 'react'
import { Dialog } from '@headlessui/react'
import Button from '../ui/Button'
import { XMarkIcon } from '@heroicons/react/24/outline'

type CreateProjectModalProps = {
  isOpen: boolean
  onClose: () => void
  onSubmit: (project: { title: string; description: string }) => void
}

const CreateProjectModal = ({ isOpen, onClose, onSubmit }: CreateProjectModalProps) => {
  const [title, setTitle] = useState('')
  const [description, setDescription] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    
    onSubmit({ 
      title: title.trim(), 
      description: description.trim() 
    })
    
    // Reset form after submission
    setTitle('')
    setDescription('')
    setIsSubmitting(false)
  }
  
  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      
      {/* Full-screen container to center the panel */}
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="bg-white rounded-lg shadow-xl max-w-md w-full">
          <div className="flex justify-between items-start p-4 border-b border-gray-200">
            <Dialog.Title className="text-lg font-semibold text-gray-900">
              Create New Project
            </Dialog.Title>
            <button
              className="text-gray-400 hover:text-gray-500"
              onClick={onClose}
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
          
          <form onSubmit={handleSubmit}>
            <div className="p-4 space-y-4">
              <div>
                <label htmlFor="title" className="block text-sm font-medium text-gray-700">
                  Project Title <span className="text-red-500">*</span>
                </label>
                <input
                  type="text"
                  id="title"
                  value={title}
                  onChange={(e) => setTitle(e.target.value)}
                  className="input-standard mt-1"
                  placeholder="My Amazing Story"
                  required
                />
              </div>
              
              <div>
                <label htmlFor="description" className="block text-sm font-medium text-gray-700">
                  Description
                </label>
                <textarea
                  id="description"
                  rows={4}
                  value={description}
                  onChange={(e) => setDescription(e.target.value)}
                  className="input-standard mt-1"
                  placeholder="A brief description of your project..."
                />
              </div>
              
              <div className="text-xs text-gray-500">
                <p>
                  All new projects start in the <span className="font-medium">Idea Phase</span>. 
                  You can advance to later phases as your project develops.
                </p>
              </div>
            </div>
            
            <div className="flex justify-end gap-2 p-4 border-t border-gray-200">
              <Button 
                variant="secondary" 
                onClick={onClose}
              >
                Cancel
              </Button>
              <Button 
                type="submit" 
                disabled={!title.trim() || isSubmitting}
                isLoading={isSubmitting}
              >
                Create Project
              </Button>
            </div>
          </form>
        </Dialog.Panel>
      </div>
    </Dialog>
  )
}

export default CreateProjectModal