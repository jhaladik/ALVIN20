// ===== FIXED CreateProjectModal.tsx =====
import { useState } from 'react'
import { Dialog } from '@headlessui/react'
import Button from '../ui/Button'
import { XMarkIcon } from '@heroicons/react/24/outline'

type CreateProjectModalProps = {
  isOpen: boolean
  onClose: () => void
  onCreateProject: (projectData: any) => Promise<void> // ✅ FIXED: Changed from onSubmit
}

const CreateProjectModal = ({ isOpen, onClose, onCreateProject }: CreateProjectModalProps) => {
  const [formData, setFormData] = useState({
    title: '',
    description: '',
    phase: 'idea' as 'idea' | 'expand' | 'story'
  })
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [error, setError] = useState('')

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    if (!formData.title.trim()) {
      setError('Project title is required')
      return
    }

    try {
      setIsSubmitting(true)
      await onCreateProject(formData) // ✅ FIXED: Use onCreateProject instead of onSubmit
      
      // Reset form on success
      setFormData({
        title: '',
        description: '',
        phase: 'idea'
      })
      onClose()
    } catch (err: any) {
      setError(err.message || 'Failed to create project')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleClose = () => {
    if (!isSubmitting) {
      setFormData({
        title: '',
        description: '',
        phase: 'idea'
      })
      setError('')
      onClose()
    }
  }

  return (
    <Dialog
      open={isOpen}
      onClose={handleClose}
      className="relative z-50"
    >
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      
      {/* Full-screen container */}
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="mx-auto max-w-md rounded-lg bg-white p-6 shadow-lg">
          {/* Header */}
          <div className="flex items-center justify-between mb-4">
            <Dialog.Title className="text-lg font-semibold text-gray-900">
              Create New Project
            </Dialog.Title>
            <button
              onClick={handleClose}
              disabled={isSubmitting}
              className="text-gray-400 hover:text-gray-600 disabled:opacity-50"
            >
              <XMarkIcon className="h-5 w-5" />
            </button>
          </div>

          {/* Error message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 border border-red-200 rounded-md">
              <p className="text-sm text-red-700">{error}</p>
            </div>
          )}

          {/* Form */}
          <form onSubmit={handleSubmit} className="space-y-4">
            {/* Title */}
            <div>
              <label htmlFor="title" className="block text-sm font-medium text-gray-700 mb-1">
                Project Title *
              </label>
              <input
                type="text"
                id="title"
                value={formData.title}
                onChange={(e) => setFormData({ ...formData, title: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Enter project title..."
                disabled={isSubmitting}
                required
              />
            </div>

            {/* Description */}
            <div>
              <label htmlFor="description" className="block text-sm font-medium text-gray-700 mb-1">
                Description
              </label>
              <textarea
                id="description"
                value={formData.description}
                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                rows={3}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                placeholder="Describe your project..."
                disabled={isSubmitting}
              />
            </div>

            {/* Phase */}
            <div>
              <label htmlFor="phase" className="block text-sm font-medium text-gray-700 mb-1">
                Starting Phase
              </label>
              <select
                id="phase"
                value={formData.phase}
                onChange={(e) => setFormData({ ...formData, phase: e.target.value as any })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-2 focus:ring-indigo-500 focus:border-indigo-500"
                disabled={isSubmitting}
              >
                <option value="idea">Idea - Just getting started</option>
                <option value="expand">Expand - Developing the concept</option>
                <option value="story">Story - Ready to write</option>
              </select>
            </div>

            {/* Actions */}
            <div className="flex gap-3 pt-4">
              <Button
                type="button"
                variant="secondary"
                onClick={handleClose}
                disabled={isSubmitting}
                className="flex-1"
              >
                Cancel
              </Button>
              <Button
                type="submit"
                variant="primary"
                isLoading={isSubmitting}
                disabled={isSubmitting || !formData.title.trim()}
                className="flex-1"
              >
                {isSubmitting ? 'Creating...' : 'Create Project'}
              </Button>
            </div>
          </form>
        </Dialog.Panel>
      </div>
    </Dialog>
  )
}

export default CreateProjectModal