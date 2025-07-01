// File: src/components/projects/InviteCollaboratorModal.tsx
import { useState, FormEvent } from 'react'
import { Dialog } from '@headlessui/react'
import Button from '../ui/Button'
import { XMarkIcon } from '@heroicons/react/24/outline'

type InviteCollaboratorModalProps = {
  isOpen: boolean
  onClose: () => void
  onSubmit: (email: string) => void
  projectTitle: string
}

const InviteCollaboratorModal = ({ 
  isOpen, 
  onClose, 
  onSubmit,
  projectTitle
}: InviteCollaboratorModalProps) => {
  const [email, setEmail] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)
  
  const handleSubmit = (e: FormEvent) => {
    e.preventDefault()
    setIsSubmitting(true)
    
    onSubmit(email.trim())
    
    // Reset form
    setEmail('')
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
              Invite Collaborator
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
              <p className="text-sm text-gray-600">
                Invite someone to collaborate on <span className="font-medium">{projectTitle}</span>.
                They will receive an email invitation.
              </p>
              
              <div>
                <label htmlFor="email" className="block text-sm font-medium text-gray-700">
                  Email Address <span className="text-red-500">*</span>
                </label>
                <input
                  type="email"
                  id="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="input-standard mt-1"
                  placeholder="collaborator@example.com"
                  required
                />
              </div>
              
              <div className="text-xs text-gray-500 border-t border-gray-200 pt-3">
                <p>
                  Collaborators can:
                </p>
                <ul className="list-disc pl-5 mt-1 space-y-1">
                  <li>View and edit project content</li>
                  <li>Add and modify scenes</li>
                  <li>Create and edit story objects</li>
                  <li>Use AI features on the project</li>
                </ul>
                <p className="mt-2">
                  Collaborators cannot delete the project or invite other collaborators.
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
                disabled={!email.trim() || isSubmitting}
                isLoading={isSubmitting}
              >
                Send Invitation
              </Button>
            </div>
          </form>
        </Dialog.Panel>
      </div>
    </Dialog>
  )
}

export default InviteCollaboratorModal