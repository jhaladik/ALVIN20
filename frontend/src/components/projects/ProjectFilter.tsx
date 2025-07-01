// File: src/components/projects/ProjectFilter.tsx
type ProjectsFilterType = 'all' | 'recent' | 'idea' | 'expand' | 'story'
type ProjectsSortType = 'newest' | 'oldest' | 'updated' | 'alphabetical'

type ProjectFilterProps = {
  activeFilter: ProjectsFilterType
  setActiveFilter: (filter: ProjectsFilterType) => void
  activeSort: ProjectsSortType
  setActiveSort: (sort: ProjectsSortType) => void
}

const ProjectFilter = ({
  activeFilter,
  setActiveFilter,
  activeSort,
  setActiveSort,
}: ProjectFilterProps) => {
  return (
    <div className="flex flex-col sm:flex-row justify-between space-y-4 sm:space-y-0 sm:items-center">
      {/* Filters */}
      <div className="flex space-x-2 overflow-x-auto pb-2 sm:pb-0">
        <button
          className={`px-3 py-1.5 text-sm rounded-full ${
            activeFilter === 'all'
              ? 'bg-indigo-100 text-indigo-800'
              : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
          }`}
          onClick={() => setActiveFilter('all')}
        >
          All Projects
        </button>
        <button
          className={`px-3 py-1.5 text-sm rounded-full ${
            activeFilter === 'recent'
              ? 'bg-indigo-100 text-indigo-800'
              : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
          }`}
          onClick={() => setActiveFilter('recent')}
        >
          Recent
        </button>
        <button
          className={`px-3 py-1.5 text-sm rounded-full ${
            activeFilter === 'idea'
              ? 'bg-blue-100 text-blue-800'
              : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
          }`}
          onClick={() => setActiveFilter('idea')}
        >
          Idea Phase
        </button>
        <button
          className={`px-3 py-1.5 text-sm rounded-full ${
            activeFilter === 'expand'
              ? 'bg-purple-100 text-purple-800'
              : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
          }`}
          onClick={() => setActiveFilter('expand')}
        >
          Expand Phase
        </button>
        <button
          className={`px-3 py-1.5 text-sm rounded-full ${
            activeFilter === 'story'
              ? 'bg-green-100 text-green-800'
              : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
          }`}
          onClick={() => setActiveFilter('story')}
        >
          Story Phase
        </button>
      </div>
      
      {/* Sort */}
      <div className="flex items-center">
        <label htmlFor="sort" className="text-sm font-medium text-gray-700 mr-2">
          Sort by:
        </label>
        <select
          id="sort"
          value={activeSort}
          onChange={(e) => setActiveSort(e.target.value as ProjectsSortType)}
          className="input-standard py-1.5 pl-3 pr-10 text-sm"
        >
          <option value="updated">Last Updated</option>
          <option value="newest">Newest</option>
          <option value="oldest">Oldest</option>
          <option value="alphabetical">Alphabetical</option>
        </select>
      </div>
    </div>
  )
}

export default ProjectFilter