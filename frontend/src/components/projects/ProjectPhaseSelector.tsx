// File: src/components/projects/ProjectPhaseSelector.tsx
import { useState } from 'react'
import {
  BookOpenIcon,
  LightBulbIcon,
  ViewfinderCircleIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline'
import { Project } from '../../types'

type ProjectPhaseSelectorProps = {
  currentPhase: Project['phase']
  onChange: (phase: Project['phase']) => void
}

const phases: Array<{
  id: Project['phase']
  name: string
  description: string
  icon: JSX.Element
  color: string
}> = [
  {
    id: 'idea',
    name: 'Idea Phase',
    description: 'Brainstorm your story concept, themes, and initial ideas.',
    icon: <LightBulbIcon className="h-8 w-8" />,
    color: 'text-blue-500 bg-blue-50'
  },
  {
    id: 'expand',
    name: 'Expand Phase',
    description: 'Develop characters, locations, and key scenes of your story.',
    icon: <ViewfinderCircleIcon className="h-8 w-8" />,
    color: 'text-purple-500 bg-purple-50'
  },
  {
    id: 'story',
    name: 'Story Phase',
    description: 'Transform your ideas and scenes into a cohesive narrative.',
    icon: <BookOpenIcon className="h-8 w-8" />,
    color: 'text-green-500 bg-green-50'
  }
]

const ProjectPhaseSelector = ({ currentPhase, onChange }: ProjectPhaseSelectorProps) => {
  const [isChanging, setIsChanging] = useState(false)
  
  const handlePhaseChange = async (phase: Project['phase']) => {
    // Don't do anything if selecting the current phase
    if (phase === currentPhase) return
    
    // Don't allow changing phase while a change is in progress
    if (isChanging) return
    
    try {
      setIsChanging(true)
      await onChange(phase)
    } finally {
      setIsChanging(false)
    }
  }

  // Find the current phase index
  const currentPhaseIndex = phases.findIndex(phase => phase.id === currentPhase)
  
  return (
    <div>
      {/* Progress bar */}
      <div className="relative mb-8">
        <div className="overflow-hidden h-2 mb-4 text-xs flex rounded bg-gray-200">
          <div
            className="shadow-none flex flex-col text-center whitespace-nowrap text-white justify-center bg-indigo-600 transition-all duration-500"
            style={{ width: `${((currentPhaseIndex + 1) / phases.length) * 100}%` }}
          ></div>
        </div>
        
        {/* Phase indicators */}
        <div className="flex justify-between">
          {phases.map((phase, index) => (
            <div 
              key={phase.id} 
              className={`flex flex-col items-center ${
                index <= currentPhaseIndex ? 'text-indigo-600' : 'text-gray-400'
              }`}
            >
              <div 
                className={`w-8 h-8 flex items-center justify-center rounded-full mb-2 ${
                  index <= currentPhaseIndex ? 'bg-indigo-100' : 'bg-gray-100'
                }`}
              >
                {index < currentPhaseIndex ? (
                  <svg className="w-5 h-5" fill="currentColor" viewBox="0 0 20 20">
                    <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                  </svg>
                ) : (
                  <span>{index + 1}</span>
                )}
              </div>
              <span className="text-xs font-medium">{phase.name}</span>
            </div>
          ))}
        </div>
      </div>
      
      {/* Phase cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {phases.map((phase, index) => {
          const isActive = phase.id === currentPhase
          const isPrevious = index < currentPhaseIndex
          const isNext = index === currentPhaseIndex + 1
          
          return (
            <div
              key={phase.id}
              className={`
                rounded-lg border p-4 transition-all cursor-pointer
                ${isActive 
                  ? 'border-indigo-500 ring-2 ring-indigo-200' 
                  : isPrevious 
                    ? 'border-gray-200 bg-gray-50 opacity-70 hover:opacity-100' 
                    : 'border-gray-200 hover:border-gray-300'
                }
              `}
              onClick={() => handlePhaseChange(phase.id)}
            >
              <div className={`rounded-full inline-flex p-3 ${phase.color} mb-3`}>
                {phase.icon}
              </div>
              
              <h3 className="text-lg font-medium text-gray-900 mb-1 flex items-center">
                {phase.name}
                {isActive && (
                  <span className="ml-2 px-2 py-0.5 bg-indigo-100 text-indigo-800 text-xs rounded-full">
                    Current
                  </span>
                )}
              </h3>
              
              <p className="text-sm text-gray-600 mb-2">
                {phase.description}
              </p>
              
              {isNext && (
                <div className="mt-2 text-sm text-indigo-600 flex items-center">
                  <span>Advance to this phase</span>
                  <ArrowRightIcon className="h-4 w-4 ml-1" />
                </div>
              )}
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default ProjectPhaseSelector