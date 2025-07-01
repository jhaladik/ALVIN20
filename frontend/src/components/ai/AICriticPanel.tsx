// File: src/components/ai/AICriticPanel.tsx
import { AIAnalysis } from '../../types'
import Button from '../ui/Button'
import LoadingSpinner from '../ui/LoadingSpinner'
import { SparklesIcon } from '@heroicons/react/24/outline'

type AICriticPanelProps = {
  sceneId: string
  aiAnalysis: AIAnalysis[]
  isAnalyzing: boolean
  activeCriticType: string
  onRequestAnalysis: (criticType: string) => void
}

const AICriticPanel = ({
  sceneId,
  aiAnalysis,
  isAnalyzing,
  activeCriticType,
  onRequestAnalysis,
}: AICriticPanelProps) => {
  // List of available AI critics
  const critics = [
    { id: 'general', name: 'General Analysis', color: 'bg-indigo-100 text-indigo-800' },
    { id: 'character', name: 'Character Development', color: 'bg-blue-100 text-blue-800' },
    { id: 'plot', name: 'Plot Coherence', color: 'bg-purple-100 text-purple-800' },
    { id: 'pacing', name: 'Pacing & Rhythm', color: 'bg-amber-100 text-amber-800' },
    { id: 'dialogue', name: 'Dialogue Evaluation', color: 'bg-green-100 text-green-800' },
    { id: 'setting', name: 'Setting & Atmosphere', color: 'bg-rose-100 text-rose-800' },
    { id: 'theme', name: 'Thematic Elements', color: 'bg-teal-100 text-teal-800' },
    { id: 'style', name: 'Style & Voice', color: 'bg-orange-100 text-orange-800' },
  ]
  
  // Get filtered analysis for the active critic
  const filteredAnalysis = aiAnalysis.filter(
    (analysis) => analysis.criticType === activeCriticType
  ).sort((a, b) => new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime())
  
  // Get date formatted for display
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString()
  }
  
  const getActiveCriticColor = () => {
    const critic = critics.find(c => c.id === activeCriticType)
    return critic?.color || 'bg-gray-100 text-gray-800'
  }
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      {/* Critics sidebar */}
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">AI Critics</h3>
        
        <div className="space-y-2">
          {critics.map((critic) => (
            <button
              key={critic.id}
              onClick={() => onRequestAnalysis(critic.id)}
              disabled={isAnalyzing}
              className={`w-full flex items-center justify-between p-3 rounded-md text-sm font-medium transition-colors ${
                activeCriticType === critic.id
                  ? 'bg-indigo-50 border border-indigo-200'
                  : 'hover:bg-gray-50 border border-transparent'
              }`}
            >
              <span>{critic.name}</span>
              <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs ${critic.color}`}>
                {aiAnalysis.filter((a) => a.criticType === critic.id).length > 0 ? 'Available' : 'New'}
              </span>
            </button>
          ))}
        </div>
        
        <div className="mt-6 text-xs text-gray-500">
          <p>Each AI critic provides specialized feedback from a different perspective.</p>
          <p className="mt-2">Running an AI analysis will use tokens from your account.</p>
        </div>
      </div>
      
      {/* Analysis content */}
      <div className="md:col-span-2">
        {isAnalyzing ? (
          <div className="card flex flex-col items-center justify-center min-h-[400px]">
            <SparklesIcon className="h-12 w-12 text-indigo-500 mb-4 animate-pulse" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">AI Analysis in Progress</h3>
            <p className="text-gray-600 text-center max-w-md mb-6">
              Our AI critic is carefully analyzing your scene from the perspective of 
              "{critics.find(c => c.id === activeCriticType)?.name}".
              This may take up to a minute.
            </p>
            <LoadingSpinner size="lg" />
          </div>
        ) : filteredAnalysis.length > 0 ? (
          <div className="card">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-medium text-gray-900 flex items-center">
                <span className={`inline-flex items-center justify-center h-6 w-6 rounded-full ${getActiveCriticColor()} mr-2 text-xs`}>
                  AI
                </span>
                {critics.find(c => c.id === activeCriticType)?.name}
              </h3>
              
              <Button
                variant="secondary"
                size="sm"
                onClick={() => onRequestAnalysis(activeCriticType)}
              >
                <SparklesIcon className="h-4 w-4 mr-1" />
                Refresh Analysis
              </Button>
            </div>
            
            <div className="space-y-6">
              {filteredAnalysis.map((analysis) => (
                <div key={analysis.id}>
                  <div className="prose max-w-none" dangerouslySetInnerHTML={{ __html: analysis.content }} />
                  
                  <p className="text-xs text-gray-500 mt-4">
                    Analysis generated on {formatDate(analysis.createdAt)}
                  </p>
                </div>
              ))}
            </div>
          </div>
        ) : (
          <div className="card flex flex-col items-center justify-center min-h-[400px]">
            <SparklesIcon className="h-12 w-12 text-gray-400 mb-4" />
            <h3 className="text-lg font-medium text-gray-900 mb-2">No Analysis Yet</h3>
            <p className="text-gray-600 text-center max-w-md mb-6">
              Get insights from our AI critic on your scene's 
              {critics.find(c => c.id === activeCriticType)?.name.toLowerCase()}.
            </p>
            <Button onClick={() => onRequestAnalysis(activeCriticType)}>
              <SparklesIcon className="h-5 w-5 mr-1" />
              Generate Analysis
            </Button>
          </div>
        )}
      </div>
    </div>
  )
}

export default AICriticPanel