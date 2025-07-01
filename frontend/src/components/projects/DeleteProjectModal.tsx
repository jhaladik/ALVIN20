// File: src/components/projects/DeleteProjectModal.tsx
import { useState } from 'react';
import { Dialog } from '@headlessui/react';
import Button from '../ui/Button';
import { XMarkIcon, ExclamationTriangleIcon } from '@heroicons/react/24/outline';

type DeleteProjectModalProps = {
  isOpen: boolean;
  onClose: () => void;
  onDelete: () => void;
  projectTitle: string;
};

const DeleteProjectModal = ({ isOpen, onClose, onDelete, projectTitle }: DeleteProjectModalProps) => {
  const [isDeleting, setIsDeleting] = useState(false);
  
  const handleDelete = async () => {
    setIsDeleting(true);
    
    try {
      await onDelete();
      onClose();
    } catch (error) {
      console.error('Error deleting project:', error);
    } finally {
      setIsDeleting(false);
    }
  };
  
  return (
    <Dialog open={isOpen} onClose={onClose} className="relative z-50">
      {/* Backdrop */}
      <div className="fixed inset-0 bg-black/30" aria-hidden="true" />
      
      {/* Full-screen container to center the panel */}
      <div className="fixed inset-0 flex items-center justify-center p-4">
        <Dialog.Panel className="bg-white rounded-lg shadow-xl max-w-md w-full">
          <div className="flex justify-between items-start p-4 border-b border-gray-200">
            <Dialog.Title className="text-lg font-semibold text-gray-900 flex items-center">
              <ExclamationTriangleIcon className="h-5 w-5 text-red-500 mr-2" />
              Delete Project
            </Dialog.Title>
            <button
              className="text-gray-400 hover:text-gray-500"
              onClick={onClose}
            >
              <XMarkIcon className="h-6 w-6" />
            </button>
          </div>
          
          <div className="p-4 space-y-4">
            <div className="text-sm text-gray-600">
              <p>
                Are you sure you want to delete <span className="font-semibold">{projectTitle}</span>?
              </p>
              <p className="mt-2">
                This action cannot be undone. All project data, including scenes, characters, and story content will be permanently removed.
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
              variant="danger"
              onClick={handleDelete}
              isLoading={isDeleting}
            >
              Delete Project
            </Button>
          </div>
        </Dialog.Panel>
      </div>
    </Dialog>
  );
};

export default DeleteProjectModal;