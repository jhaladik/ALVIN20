// File: src/components/projects/ProjectCard.tsx
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { Project } from '../../types'
import { 
  PencilIcon, 
  TrashIcon, 
  EllipsisVerticalIcon,
  ClockIcon,
  UserGroupIcon,
} from '@heroicons/react/24/outline'
import { Menu } from '@headlessui/react'

type ProjectCardProps = {
  project: Project
  onDelete: () => void
}

const ProjectCard = ({ project, onDelete }: ProjectCardProps) => {
  const [isHovered, setIsHovered] = useState(false)
  
  const getPhaseColor = (phase: string) => {
    switch (phase) {
      case 'idea':
        return 'bg-blue-100 text-blue-800'
      case 'expand':
        return 'bg-purple-100 text-purple-800'
      case 'story':
        return 'bg-green-100 text-green-800'
      default:
        return 'bg-gray-100 text-gray-800'
    }
  }
  
  const formatLastModified = (date: string) => {
    const now = new Date()
    const modifiedDate = new Date(date)
    const diffTime = Math.abs(now.getTime() - modifiedDate.getTime())
    const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))
    
    if (diffDays === 0) {
      return 'Today'
    } else if (diffDays === 1) {
      return 'Yesterday'
    } else if (diffDays < 7) {
      return `${diffDays} days ago`
    } else if (diffDays < 30) {
      return `${Math.floor(diffDays / 7)} weeks ago`
    } else {
      return modifiedDate.toLocaleDateString()
    }
  }
  
  return (
    <div
      className="card hover:shadow-md transition-shadow relative"
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Card menu */}
      <Menu as="div" className="absolute top-3 right-3 z-10">
        <Menu.Button className="flex items-center justify-center h-8 w-8 rounded-full hover:bg-gray-100">
          <EllipsisVerticalIcon className="h-5 w-5 text-gray-500" />
        </Menu.Button>
        <Menu.Items className="absolute right-0 mt-1 w-48 bg-white rounded-md shadow-lg z-10 border border-gray-200 divide-y divide-gray-100">
          <div className="py-1">
            <Menu.Item>
              {({ active }) => (
                <Link
                  to={`/projects/${project.id}/edit`}
                  className={`${
                    active ? 'bg-gray-100' : ''
                  } flex items-center px-4 py-2 text-sm text-gray-700 w-full text-left`}
                >
                  <PencilIcon className="h-4 w-4 mr-2" />
                  Edit Project
                </Link>
              )}
            </Menu.Item>
          </div>
          <div className="py-1">
            <Menu.Item>
              {({ active }) => (
                <button
                  onClick={onDelete}
                  className={`${
                    active ? 'bg-red-50' : ''
                  } flex items-center px-4 py-2 text-sm text-red-600 w-full text-left`}
                >
                  <TrashIcon className="h-4 w-4 mr-2" />
                  Delete Project
                </button>
              )}
            </Menu.Item>
          </div>
        </Menu.Items>
      </Menu>

      {/* Phase badge */}
      <div className={`absolute top-3 left-3 text-xs font-medium px-2 py-1 rounded-full ${getPhaseColor(project.phase)}`}>
        {project.phase === 'idea' && 'Idea Phase'}
        {project.phase === 'expand' && 'Expand Phase'}
        {project.phase === 'story' && 'Story Phase'}
      </div>
      
      {/* Card content */}
      <div className="pt-10"> {/* Add padding to account for the absolute positioned elements */}
        <Link to={`/projects/${project.id}`} className="block">
          <h3 className="text-lg font-medium text-gray-900 line-clamp-2">{project.title}</h3>
          <p className="mt-2 text-sm text-gray-600 line-clamp-3">{project.description}</p>
          
          {/* Progress bar */}
          <div className="mt-4">
            <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
              <span>Progress</span>
              <span>{project.progress}%</span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div 
                className="bg-indigo-600 h-2 rounded-full" 
                style={{ width: `${project.progress}%` }}
              ></div>
            </div>
          </div>
          
          {/* Metadata */}
          <div className="mt-4 pt-4 border-t border-gray-100 flex justify-between text-xs text-gray-500">
            <div className="flex items-center">
              <ClockIcon className="h-4 w-4 mr-1" />
              {formatLastModified(project.lastModified)}
            </div>
            
            {project.collaborators.length > 0 && (
              <div className="flex items-center">
                <UserGroupIcon className="h-4 w-4 mr-1" />
                {project.collaborators.length} 
                {project.collaborators.length === 1 ? ' collaborator' : ' collaborators'}
              </div>
            )}
          </div>
        </Link>
      </div>
    </div>
  )
}

export default ProjectCard