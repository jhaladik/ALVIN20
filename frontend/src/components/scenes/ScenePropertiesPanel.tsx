// File: src/components/scenes/ScenePropertiesPanel.tsx
import { Scene } from '../../types'

type ScenePropertiesPanelProps = {
  scene: Scene
  onUpdate: (properties: Partial<Scene>) => void
}

const ScenePropertiesPanel = ({ scene, onUpdate }: ScenePropertiesPanelProps) => {
  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Basic Properties</h3>
        
        <div className="space-y-4">
          <div>
            <label htmlFor="scene-title" className="block text-sm font-medium text-gray-700 mb-1">
              Scene Title
            </label>
            <input
              id="scene-title"
              type="text"
              value={scene.title}
              onChange={(e) => onUpdate({ title: e.target.value })}
              className="input-standard"
            />
          </div>
          
          <div>
            <label htmlFor="scene-order" className="block text-sm font-medium text-gray-700 mb-1">
              Scene Order
            </label>
            <input
              id="scene-order"
              type="number"
              min="1"
              value={scene.order}
              onChange={(e) => onUpdate({ order: parseInt(e.target.value) })}
              className="input-standard"
            />
            <p className="text-xs text-gray-500 mt-1">
              The order determines where this scene appears in the story sequence.
            </p>
          </div>
          
          <div>
            <label htmlFor="emotional-intensity" className="block text-sm font-medium text-gray-700 mb-1">
              Emotional Intensity ({scene.emotionalIntensity}/10)
            </label>
            <input
              id="emotional-intensity"
              type="range"
              min="1"
              max="10"
              value={scene.emotionalIntensity}
              onChange={(e) => onUpdate({ emotionalIntensity: parseInt(e.target.value) })}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Subtle</span>
              <span>Moderate</span>
              <span>Intense</span>
            </div>
          </div>
        </div>
      </div>
      
      <div className="card">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Scene Relationships</h3>
        
        <div className="space-y-6">
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Characters in this Scene</h4>
            <div className="flex flex-wrap gap-2">
              {scene.characters.length > 0 ? (
                scene.characters.map(charId => {
                  const character = charId
                  return (
                    <div 
                      key={charId}
                      className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800"
                    >
                      {character}
                    </div>
                  )
                })
              ) : (
                <p className="text-sm text-gray-500">No characters selected</p>
              )}
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Locations in this Scene</h4>
            <div className="flex flex-wrap gap-2">
              {scene.locations.length > 0 ? (
                scene.locations.map(locId => {
                  const location = locId
                  return (
                    <div 
                      key={locId}
                      className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-purple-100 text-purple-800"
                    >
                      {location}
                    </div>
                  )
                })
              ) : (
                <p className="text-sm text-gray-500">No locations selected</p>
              )}
            </div>
          </div>
          
          <div>
            <h4 className="text-sm font-medium text-gray-700 mb-2">Props in this Scene</h4>
            <div className="flex flex-wrap gap-2">
              {scene.props.length > 0 ? (
                scene.props.map(propId => {
                  const prop = propId
                  return (
                    <div 
                      key={propId}
                      className="inline-flex items-center px-2.5 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800"
                    >
                      {prop}
                    </div>
                  )
                })
              ) : (
                <p className="text-sm text-gray-500">No props selected</p>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ScenePropertiesPanel