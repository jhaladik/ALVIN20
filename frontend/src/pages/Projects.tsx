// File: src/pages/Projects.tsx
import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../services/api'
import { Project } from '../types'
import LoadingSpinner from '../components/ui/LoadingSpinner'
import Button from '../components/ui/Button'
import ProjectCard from '../components/projects/ProjectCard'
import ProjectFilter from '../components/projects/ProjectFilter'
import CreateProjectModal from '../components/projects/CreateProjectModal'
import { useSearchParams } from 'react-router-dom'
import {
  PlusIcon,
  SparklesIcon,
} from '@heroicons/react/24/outline'

type ProjectsFilterType = 'all' | 'recent' | 'idea' | 'expand' | 'story'
type ProjectsSortType = 'newest' | 'oldest' | 'updated' | 'alphabetical'

const Projects = () => {
  const [projects, setProjects] = useState<Project[]>([])
  const [filteredProjects, setFilteredProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [error, setError] = useState('')
  const [isCreateModalOpen, setIsCreateModalOpen] = useState(false)
  const [activeFilter, setActiveFilter] = useState<ProjectsFilterType>('all')
  const [activeSort, setActiveSort] = useState<ProjectsSortType>('updated')
  const [searchParams, setSearchParams] = useSearchParams()
  const searchQuery = searchParams.get('search') || ''
  
  useEffect(() => {
    const loadProjects = async () => {
      try {
        setIsLoading(true)
        const response = await api.get('/api/projects')
        setProjects(response.data)
      } catch (err) {
        console.error('Failed to load projects', err)
        setError('Failed to load projects. Please try again.')
      } finally {
        setIsLoading(false)
      }
    }
    
    loadProjects()
  }, [])
  
  // Filter and sort projects whenever these values change
  useEffect(() => {
    let result = [...projects]
    
    // Apply search filter if present
    if (searchQuery) {
      result = result.filter(p => 
        p.title.toLowerCase().includes(searchQuery.toLowerCase()) || 
        p.description.toLowerCase().includes(searchQuery.toLowerCase())
      )
    }
    
    // Apply phase filter
    if (activeFilter !== 'all' && activeFilter !== 'recent') {
      result = result.filter(p => p.phase === activeFilter)
    } else if (activeFilter === 'recent') {
      // Show last 5 modified projects
      result = result.sort((a, b) => 
        new Date(b.lastModified).getTime() - new Date(a.lastModified).getTime()
      ).slice(0, 5)
    }
    
    // Apply sorting
    result = sortProjects(result, activeSort)
    
    setFilteredProjects(result)
  }, [projects, activeFilter, activeSort, searchQuery])
  
  const sortProjects = (projects: Project[], sortType: ProjectsSortType): Project[] => {
    switch (sortType) {
      case 'newest':
        return [...projects].sort((a, b) => 
          new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime()
        )
      case 'oldest':
        return [...projects].sort((a, b) => 
          new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime()
        )
      case 'updated':
        return [...projects].sort((a, b) => 
          new Date(b.lastModified).getTime() - new Date(a.lastModified).getTime()
        )
      case 'alphabetical':
        return [...projects].sort((a, b) => a.title.localeCompare(b.title))
      default:
        return projects
    }
  }
  
  const handleCreateProject = async (project: { title: string; description: string }) => {
    try {
      setIsLoading(true)
      const response = await api.post('/api/projects', project)
      setProjects(prevProjects => [...prevProjects, response.data])
      setIsCreateModalOpen(false)
    } catch (err) {
      console.error('Failed to create project', err)
      setError('Failed to create project. Please try again.')
    } finally {
      setIsLoading(false)
    }
  }
  
  const handleDeleteProject = async (projectId: string) => {
    if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
      return
    }
    
    try {
      await api.delete(`/api/projects/${projectId}`)
      setProjects(prevProjects => prevProjects.filter(p => p.id !== projectId))
    } catch (err) {
      console.error('Failed to delete project', err)
      setError('Failed to delete project. Please try again.')
    }
  }
  
  const handleSearch = (query: string) => {
    if (query) {
      setSearchParams({ search: query })
    } else {
      setSearchParams({})
    }
  }
  
  if (isLoading && projects.length === 0) {
    return (
      <div className="flex justify-center items-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    )
  }
  
  return (
    <div className="space-y-6">
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4">
          <p className="text-sm text-red-700">{error}</p>
        </div>
      )}
      
      {/* Projects header */}
      <div className="flex flex-col md:flex-row md:justify-between md:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Your Projects</h1>
          <p className="text-gray-600">Manage all your writing projects</p>
        </div>
        
        <div className="flex gap-2">
          <div className="relative">
            <input
              type="search"
              placeholder="Search projects..."
              className="input-standard pl-10"
              value={searchQuery}
              onChange={(e) => handleSearch(e.target.value)}
            />
            <div className="absolute inset-y-0 left-0 flex items-center pl-3 pointer-events-none">
              <svg className="w-5 h-5 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
              </svg>
            </div>
          </div>
          
          <Button 
            onClick={() => setIsCreateModalOpen(true)}
            className="whitespace-nowrap"
          >
            <PlusIcon className="h-5 w-5 mr-1" />
            New Project
          </Button>
        </div>
      </div>
      
      {/* Filters */}
      <ProjectFilter 
        activeFilter={activeFilter}
        setActiveFilter={setActiveFilter}
        activeSort={activeSort}
        setActiveSort={setActiveSort}
      />
      
      {/* Projects grid */}
      {filteredProjects.length > 0 ? (
        <div className="grid gap-4 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3">
          {filteredProjects.map(project => (
            <ProjectCard
              key={project.id}
              project={project}
              onDelete={() => handleDeleteProject(project.id)}
            />
          ))}
        </div>
      ) : (
        <div className="text-center py-16 border border-dashed border-gray-300 rounded-md">
          <SparklesIcon className="h-12 w-12 text-gray-400 mx-auto" />
          <h3 className="mt-4 text-sm font-medium text-gray-900">
            {searchQuery 
              ? 'No projects match your search' 
              : projects.length === 0 
                ? 'No projects yet' 
                : 'No projects match your filter'}
          </h3>
          <p className="mt-1 text-sm text-gray-500">
            {searchQuery 
              ? 'Try a different search term' 
              : projects.length === 0 
                ? 'Get started by creating a new project' 
                : 'Try a different filter'}
          </p>
          {!searchQuery && projects.length === 0 && (
            <div className="mt-6">
              <Button onClick={() => setIsCreateModalOpen(true)}>
                <PlusIcon className="h-5 w-5 mr-1" />
                Create New Project
              </Button>
            </div>
          )}
        </div>
      )}
      
      {/* Create project modal */}
      <CreateProjectModal
        isOpen={isCreateModalOpen}
        onClose={() => setIsCreateModalOpen(false)}
        onSubmit={handleCreateProject}
      />
    </div>
  )
}

export default Projects