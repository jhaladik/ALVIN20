
import React, { useReducer, useEffect } from 'react'

interface Collaborator {
  id: string
  name: string
  email: string
  status: 'online' | 'offline' | 'typing'
  avatar?: string
}

interface CollaboratorsState {
  collaborators: Collaborator[]
  loading: boolean
  error: string | null
  filter: 'all' | 'online' | 'offline'
}

type CollaboratorsAction = 
  | { type: 'LOADING'; payload: boolean }
  | { type: 'SET_COLLABORATORS'; payload: Collaborator[] }
  | { type: 'ADD_COLLABORATOR'; payload: Collaborator }
  | { type: 'UPDATE_COLLABORATOR'; payload: { id: string; updates: Partial<Collaborator> } }
  | { type: 'REMOVE_COLLABORATOR'; payload: string }
  | { type: 'SET_FILTER'; payload: CollaboratorsState['filter'] }
  | { type: 'SET_ERROR'; payload: string | null }

const collaboratorsReducer = (state: CollaboratorsState, action: CollaboratorsAction): CollaboratorsState => {
  switch (action.type) {
    case 'LOADING':
      return { ...state, loading: action.payload }
    
    case 'SET_COLLABORATORS':
      return { ...state, collaborators: action.payload, loading: false, error: null }
    
    case 'ADD_COLLABORATOR':
      return { 
        ...state, 
        collaborators: [...state.collaborators, action.payload] 
      }
    
    case 'UPDATE_COLLABORATOR':
      return {
        ...state,
        collaborators: state.collaborators.map(collab =>
          collab.id === action.payload.id 
            ? { ...collab, ...action.payload.updates }
            : collab
        )
      }
    
    case 'REMOVE_COLLABORATOR':
      return {
        ...state,
        collaborators: state.collaborators.filter(collab => collab.id !== action.payload)
      }
    
    case 'SET_FILTER':
      return { ...state, filter: action.payload }
    
    case 'SET_ERROR':
      return { ...state, error: action.payload, loading: false }
    
    default:
      return state
  }
}

const CollaboratorsList: React.FC<{ projectId: string }> = ({ projectId }) => {
  const [state, dispatch] = useReducer(collaboratorsReducer, {
    collaborators: [],
    loading: true,
    error: null,
    filter: 'all'
  })

  // Much cleaner than multiple useState hooks!
  
  const filteredCollaborators = state.collaborators.filter(collab => {
    switch (state.filter) {
      case 'online': return collab.status === 'online' || collab.status === 'typing'
      case 'offline': return collab.status === 'offline'
      default: return true
    }
  })

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <header className="flex justify-between items-center mb-4">
        <h2 className="text-lg font-semibold text-gray-900">
          Collaborators ({filteredCollaborators.length})
        </h2>
        
        <select 
          value={state.filter}
          onChange={(e) => dispatch({ type: 'SET_FILTER', payload: e.target.value as any })}
          className="text-sm border border-gray-300 rounded-md px-2 py-1"
          aria-label="Filter collaborators"
        >
          <option value="all">All</option>
          <option value="online">Online</option>
          <option value="offline">Offline</option>
        </select>
      </header>

      {state.loading && (
        <div className="text-center py-4" aria-live="polite">
          Loading collaborators...
        </div>
      )}

      {state.error && (
        <div className="text-red-600 text-sm py-2" role="alert">
          {state.error}
        </div>
      )}

      <ul className="space-y-2" role="list">
        {filteredCollaborators.map(collaborator => (
          <li key={collaborator.id} className="flex items-center space-x-3 py-2">
            <div className={`w-3 h-3 rounded-full ${
              collaborator.status === 'online' ? 'bg-green-400' :
              collaborator.status === 'typing' ? 'bg-yellow-400 animate-pulse' :
              'bg-gray-400'
            }`} aria-hidden="true" />
            
            <div className="flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {collaborator.name}
              </p>
              <p className="text-sm text-gray-500 truncate">
                {collaborator.email}
              </p>
            </div>
            
            <span className={`text-xs px-2 py-1 rounded-full ${
              collaborator.status === 'online' ? 'bg-green-100 text-green-800' :
              collaborator.status === 'typing' ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              {collaborator.status === 'typing' ? 'Typing...' : collaborator.status}
            </span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default CollaboratorsList