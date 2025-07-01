// File: src/components/scenes/SceneObjectSelector.tsx
import { ReactNode, useState } from 'react'
import { StoryObject } from '../../types'
import { PlusIcon, ChevronUpIcon, ChevronDownIcon } from '@heroicons/react/24/outline'
import { Link } from 'react-router-dom'
import { useParams } from 'react-router-dom'

type SceneObjectSelectorProps = {
  title: string
  icon: ReactNode
  selectedIds: string[]
  objects: StoryObject[]
  onChange: (ids: string[]) => void
}

const SceneObjectSelector = ({ 
  title, 
  icon, 
  selectedIds, 
  objects, 
  onChange 
}: SceneObjectSelectorProps) => {
  const { projectId } = useParams<{ projectId: string }>()
  const [isExpanded, setIsExpanded] = useState(true)
  
  const toggleSelection = (id: string) => {
    if (selectedIds.includes(id)) {
      onChange(selectedIds.filter(selectedId => selectedId !== id))
    } else {
      onChange([...selectedIds, id])
    }
  }
  
  return (
    <div className="card">
      <div 
        className="flex items-center justify-between cursor-pointer" 
        onClick={() => setIsExpanded(!isExpanded)}
      >
        <h3 className="text-sm font-medium text-gray-700 flex items-center">
          {icon}
          <span className="ml-2">{title}</span>
          <span className="ml-2 text-xs text-gray-500">
            ({selectedIds.length}/{objects.length})
          </span>
        </h3>
        {isExpanded ? (
          <ChevronUpIcon className="h-5 w-5 text-gray-400" />
        ) : (
          <ChevronDownIcon className="h-5 w-5 text-gray-400" />
        )}
      </div>
      
      {isExpanded && (
        <div className="mt-3 space-y-2">
          {objects.length > 0 ? (
            objects.map(obj => (
              <div 
                key={obj.id} 
                className={`flex items-center rounded-md p-2 cursor-pointer transition-colors ${
                  selectedIds.includes(obj.id) 
                    ? 'bg-indigo-50 border border-indigo-200'
                    : 'hover:bg-gray-50 border border-transparent'
                }`}
                onClick={() => toggleSelection(obj.id)}
              >
                <input
                  type="checkbox"
                  checked={selectedIds.includes(obj.id)}
                  onChange={() => toggleSelection(obj.id)}
                  className="h-4 w-4 text-indigo-600 focus:ring-indigo-500 border-gray-300 rounded mr-3"
                />
                <div className="flex-1 overflow-hidden">
                  <p className="text-sm font-medium text-gray-900 truncate">{obj.name}</p>
                </div>
              </div>
            ))
          ) : (
            <div className="text-sm text-gray-500 text-center py-2">
              No {title.toLowerCase()} available
            </div>
          )}
          
          <Link
            to={`/projects/${projectId}/objects?type=${title.toLowerCase()}`}
            className="flex items-center justify-center w-full text-sm text-indigo-600 hover:text-indigo-500 font-medium mt-2 py-1"
          >
            <PlusIcon className="h-4 w-4 mr-1" />
            Add New {title.slice(0, -1)}
          </Link>
        </div>
      )}
    </div>
  )
}

export default SceneObjectSelector