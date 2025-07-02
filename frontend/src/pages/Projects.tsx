// File: src/pages/Projects.tsx - FIXED TO MATCH YOUR BACKEND ENDPOINTS
import React, { useState, useEffect, useCallback } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../services/api'
import { Project } from '../types'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import Button from '../components/ui/Button'
import ProjectCard from '../components/projects/ProjectCard'
import ProjectFilter from '../components/projects/ProjectFilter'
import CreateProjectModal from '../components/projects/CreateProjectModal'
import {
  PlusIcon,
  SparklesIcon,
  ExclamationCircleIcon,
  MagnifyingGlassIcon,
  XMarkIcon,
} from '@heroicons/react/24/outline'

// Updated types to match your backend
type ProjectsFilterType = 'all' | 'recent' | 'idea' | 'expand' | 'story'
type ProjectsSortType = 'newest' | 'oldest' | 'updated' | 'alphabetical'

interface ProjectsState {
  projects: Project[]
  filteredProjects: Project[]
  isLoading: boolean
  error: string
  isCreateModalOpen: boolean
  activeFilter: ProjectsFilterType
  activeSort: ProjectsSortType
}

const Projects: React.FC = () => {
  // Consolidated state management
  const [state, setState] = useState<ProjectsState>({
    projects: [],
    filteredProjects: [],
    isLoading: true,
    error: '',
    isCreateModalOpen: false,
    activeFilter: 'all',
    activeSort: 'updated',
  })

  const [searchParams, setSearchParams] = useSearchParams()
  const searchQuery = searchParams.get('search') || ''

  // Update state helper
  const updateState = useCallback((updates: Partial<ProjectsState>) => {
    setState(prevState => ({ ...prevState, ...updates }))
  }, [])

  // Load projects - FIXED to match your backend API
  const loadProjects = useCallback(async () => {
    try {
      updateState({ isLoading: true, error: '' })
      
      console.log('🔍 Loading projects from backend...')
      const response = await api.get('/api/projects')
      
      console.log('📡 Backend response:', response.data)
      
      // Your backend returns { "projects": [...] }
      const projectsData = response.data?.projects || []
      
      if (Array.isArray(projectsData)) {
        console.log(`✅ Loaded ${projectsData.length} projects successfully`)
        updateState({ projects: projectsData })
      } else {
        console.error('❌ Expected projects array, got:', typeof projectsData, projectsData)
        updateState({ 
          error: 'Server returned unexpected data format. Please contact support.' 
        })
      }
      
    } catch (err: any) {
      console.error('❌ Failed to load projects:', err)
      
      // Enhanced error handling based on your backend responses
      let errorMessage = 'Failed to load projects. Please try again.'
      
      if (err.response) {
        const status = err.response.status
        const data = err.response.data
        
        console.log(`🚨 API Error ${status}:`, data)
        
        switch (status) {
          case 401:
            errorMessage = 'Authentication required. Please log in to view your projects.'
            // You might want to redirect to login here
            break
          case 403:
            errorMessage = 'You do not have permission to view projects.'
            break
          case 404:
            errorMessage = 'Projects endpoint not found. Please check your API configuration.'
            break
          case 500:
            errorMessage = data?.message || 'Server error. Please try again later.'
            break
          default:
            errorMessage = data?.message || `Server error (${status}). Please try again.`
        }
      } else if (err.request) {
        console.log('🌐 Network error - no response received')
        errorMessage = 'Cannot connect to server. Please check if the backend is running and your internet connection.'
      } else if (err.code === 'NETWORK_ERROR') {
        errorMessage = 'Network error. Please check your connection and try again.'
      } else {
        console.log('🔧 Request setup error:', err.message)
        errorMessage = 'Request configuration error. Please refresh the page.'
      }
      
      updateState({ error: errorMessage })
      
    } finally {
      // CRITICAL: Always set loading to false, regardless of success or failure
      updateState({ isLoading: false })
      console.log('✅ Projects loading process completed')
    }
  }, [updateState])

  // Initial load
  useEffect(() => {
    loadProjects()
  }, [loadProjects])

  // Filter and sort projects - UPDATED for your backend data structure
  const applyFiltersAndSort = useCallback(() => {
    let result = [...state.projects]
    
    // Apply search filter
    if (searchQuery.trim()) {
      const query = searchQuery.toLowerCase().trim()
      result = result.filter(project => 
        project.title.toLowerCase().includes(query) || 
        (project.description && project.description.toLowerCase().includes(query)) ||
        (project.genre && project.genre.toLowerCase().includes(query))
      )
    }
    
    // Apply phase filter - using 'current_phase' from your backend
    switch (state.activeFilter) {
      case 'recent':
        result = result
          .sort((a, b) => new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime())
          .slice(0, 5)
        break
      case 'idea':
      case 'expand': 
      case 'story':
        result = result.filter(project => project.current_phase === state.activeFilter)
        break
      case 'all':
      default:
        // No additional filtering
        break
    }
    
    // Apply sorting (unless already sorted by recent filter)
    if (state.activeFilter !== 'recent') {
      result = sortProjects(result, state.activeSort)
    }
    
    updateState({ filteredProjects: result })
  }, [state.projects, state.activeFilter, state.activeSort, searchQuery, updateState])

  // Apply filters whenever dependencies change
  useEffect(() => {
    applyFiltersAndSort()
  }, [applyFiltersAndSort])

  // Sorting function - UPDATED for your backend field names
  const sortProjects = (projects: Project[], sortType: ProjectsSortType): Project[] => {
    switch (sortType) {
      case 'newest':
        return [...projects].sort((a, b) => 
          new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
        )
      case 'oldest':
        return [...projects].sort((a, b) => 
          new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        )
      case 'updated':
        return [...projects].sort((a, b) => 
          new Date(b.updated_at).getTime() - new Date(a.updated_at).getTime()
        )
      case 'alphabetical':
        return [...projects].sort((a, b) => a.title.localeCompare(b.title))
      default:
        return projects
    }
  }

  // Create new project - FIXED for your backend response format
  const handleCreateProject = async (projectData: { title: string; description: string; [key: string]: any }) => {
    try {
      updateState({ isLoading: true, error: '' })
      
      console.log('📝 Creating project:', projectData)
      const response = await api.post('/api/projects', projectData)
      
      console.log('✅ Project creation response:', response.data)
      
      // Your backend might return { "project": newProject } or { "success": true, "project": newProject }
      const newProject = response.data?.project || response.data
      
      if (newProject && newProject.id) {
        console.log('🎉 New project created:', newProject.title)
        updateState({ 
          projects: [...state.projects, newProject],
          isCreateModalOpen: false 
        })
      } else {
        console.error('❌ Invalid project creation response:', response.data)
        throw new Error('Invalid response format from server')
      }
      
    } catch (err: any) {
      console.error('❌ Failed to create project:', err)
      
      let errorMessage = 'Failed to create project. Please try again.'
      
      if (err.response?.data?.message) {
        errorMessage = err.response.data.message
      } else if (err.response?.status === 401) {
        errorMessage = 'Please log in to create projects.'
      } else if (err.response?.status === 400) {
        errorMessage = 'Invalid project data. Please check all required fields.'
      }
      
      updateState({ error: errorMessage })
      
    } finally {
      updateState({ isLoading: false })
    }
  }

  // Delete project - UPDATED for your backend endpoint
  const handleDeleteProject = async (projectId: string) => {
    if (!window.confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      return
    }
    
    try {
      console.log('🗑️ Deleting project:', projectId)
      
      // Your backend DELETE /api/projects/{id} returns { "success": true, "message": "..." }
      const response = await api.delete(`/api/projects/${projectId}`)
      
      console.log('✅ Project deletion response:', response.data)
      
      if (response.data?.success) {
        updateState({ 
          projects: state.projects.filter(p => p.id !== projectId),
          error: ''
        })
        console.log('🎉 Project deleted successfully')
      } else {
        throw new Error('Deletion not confirmed by server')
      }
      
    } catch (err: any) {
      console.error('❌ Failed to delete project:', err)
      updateState({ 
        error: err.response?.data?.message || 'Failed to delete project. Please try again.'
      })
    }
  }

  // Search handler
  const handleSearch = (query: string) => {
    if (query.trim()) {
      setSearchParams({ search: query })
    } else {
      setSearchParams({})
    }
  }

  // Clear search
  const clearSearch = () => {
    setSearchParams({})
  }

  // Filter handlers
  const handleFilterChange = (filter: ProjectsFilterType) => {
    updateState({ activeFilter: filter })
  }

  const handleSortChange = (sort: ProjectsSortType) => {
    updateState({ activeSort: sort })
  }

  // Retry handler
  const handleRetry = () => {
    console.log('🔄 Retrying projects load...')
    loadProjects()
  }

  // Loading state
  if (state.isLoading && state.projects.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
        <span className="ml-3 text-gray-600">Loading your projects...</span>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Error Banner */}
      {state.error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 rounded-md">
          <div className="flex items-center">
            <ExclamationCircleIcon className="h-5 w-5 text-red-500 mr-2" />
            <div className="flex-1">
              <p className="text-sm text-red-700">{state.error}</p>
            </div>
            <Button 
              variant="outline" 
              size="sm" 
              onClick={handleRetry}
              className="ml-4"
            >
              Retry
            </Button>
          </div>
        </div>
      )}
      
      {/* Header */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Your Projects</h1>
          <p className="text-gray-600">
            {state.projects.length === 0 
              ? 'Start your writing journey by creating your first project'
              : `Manage all your writing projects (${state.projects.length} total)`
            }
          </p>
        </div>
        
        <div className="flex gap-2">
          {/* Search Input */}
          <div className="relative">
            <input
              type="search"
              placeholder="Search projects..."
              className="input-standard pl-10 pr-10 min-w-[250px]"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
            />
            <MagnifyingGlassIcon className="absolute left-3 top-1/2 transform -translate-y-1/2 h-5 w-5 text-gray-400" />
            {searchQuery && (
              <button
                onClick={clearSearch}
                className="absolute right-3 top-1/2 transform -translate-y-1/2"
              >
                <XMarkIcon className="h-5 w-5 text-gray-400 hover:text-gray-600" />
              </button>
            )}
          </div>
          
          <Button 
            onClick={() => updateState({ isCreateModalOpen: true })}
            className="whitespace-nowrap"
            disabled={state.isLoading}
          >
            <PlusIcon className="h-5 w-5 mr-1" />
            New Project
          </Button>
        </div>
      </div>
      
      {/* Filters */}
      {state.projects.length > 0 && (
        <ProjectFilter 
          activeFilter={state.activeFilter}
          setActiveFilter={handleFilterChange}
          activeSort={state.activeSort}
          setActiveSort={handleSortChange}
        />
      )}
      
      {/* Projects Grid or Empty State */}
      {state.projects.length === 0 && !state.isLoading ? (
        <div className="text-center py-12">
          <SparklesIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No projects yet</h3>
          <p className="text-gray-500 mb-6">
            Create your first project to start your writing journey with AI assistance.
          </p>
          <Button 
            onClick={() => updateState({ isCreateModalOpen: true })}
            size="lg"
          >
            <PlusIcon className="h-5 w-5 mr-2" />
            Create Your First Project
          </Button>
        </div>
      ) : state.filteredProjects.length === 0 && searchQuery ? (
        <div className="text-center py-12">
          <MagnifyingGlassIcon className="h-12 w-12 text-gray-400 mx-auto mb-4" />
          <h3 className="text-lg font-medium text-gray-900 mb-2">No projects found</h3>
          <p className="text-gray-500 mb-4">
            No projects match your search for "{searchQuery}"
          </p>
          <Button variant="outline" onClick={clearSearch}>
            Clear Search
          </Button>
        </div>
      ) : state.filteredProjects.length === 0 && state.activeFilter !== 'all' ? (
        <div className="text-center py-12">
          <h3 className="text-lg font-medium text-gray-900 mb-2">No projects in this category</h3>
          <p className="text-gray-500 mb-4">
            No projects found for the "{state.activeFilter}" filter.
          </p>
          <Button variant="outline" onClick={() => handleFilterChange('all')}>
            Show All Projects
          </Button>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
          {state.filteredProjects.map((project) => (
            <ProjectCard
              key={project.id}
              project={project}
              onDelete={() => handleDeleteProject(project.id)}
            />
          ))}
        </div>
      )}
      
      {/* Loading overlay for operations */}
      {state.isLoading && state.projects.length > 0 && (
        <div className="fixed inset-0 bg-black bg-opacity-25 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg shadow-lg">
            <LoadingSpinner size="md" />
            <p className="mt-2 text-gray-600">Processing...</p>
          </div>
        </div>
      )}
      
      {/* Create Project Modal */}
      {state.isCreateModalOpen && (
        <CreateProjectModal
          isOpen={state.isCreateModalOpen}
          onClose={() => updateState({ isCreateModalOpen: false })}
          onSubmit={handleCreateProject}
        />
      )}
    </div>
  )
}

export default Projects