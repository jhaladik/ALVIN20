// File: src/components/projects/ProjectDetailTabs.tsx
type ActiveTabType = 'overview' | 'scenes' | 'objects' | 'ai'

type ProjectDetailTabsProps = {
  activeTab: ActiveTabType
  setActiveTab: (tab: ActiveTabType) => void
}

const ProjectDetailTabs = ({ activeTab, setActiveTab }: ProjectDetailTabsProps) => {
  return (
    <div className="border-b border-gray-200">
      <nav className="-mb-px flex space-x-8">
        <button
          className={`py-4 px-1 border-b-2 font-medium text-sm ${
            activeTab === 'overview'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          }`}
          onClick={() => setActiveTab('overview')}
        >
          Overview
        </button>
        <button
          className={`py-4 px-1 border-b-2 font-medium text-sm ${
            activeTab === 'scenes'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          }`}
          onClick={() => setActiveTab('scenes')}
        >
          Scenes
        </button>
        <button
          className={`py-4 px-1 border-b-2 font-medium text-sm ${
            activeTab === 'objects'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          }`}
          onClick={() => setActiveTab('objects')}
        >
          Story Objects
        </button>
        <button
          className={`py-4 px-1 border-b-2 font-medium text-sm ${
            activeTab === 'ai'
              ? 'border-indigo-600 text-indigo-600'
              : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
          }`}
          onClick={() => setActiveTab('ai')}
        >
          AI Workshop
        </button>
      </nav>
    </div>
  )
}

export default ProjectDetailTabs