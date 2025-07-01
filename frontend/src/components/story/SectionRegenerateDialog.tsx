// src/components/story/SectionRegenerateDialog.tsx
import React, { useState } from 'react';
import { NarrativeOptions } from '../../types';
import { XIcon, RefreshIcon } from '@heroicons/react/24/outline';

interface SectionRegenerateDialogProps {
  currentOptions: NarrativeOptions;
  onRegenerate: (options: Partial<NarrativeOptions>) => void;
  onClose: () => void;
}

const SectionRegenerateDialog: React.FC<SectionRegenerateDialogProps> = ({
  currentOptions,
  onRegenerate,
  onClose
}) => {
  const [options, setOptions] = useState<NarrativeOptions>(currentOptions);
  
  const narrativeVoiceOptions = [
    { id: 'first_person', label: 'First Person' },
    { id: 'third_person_limited', label: 'Third Person Limited' },
    { id: 'third_person_omniscient', label: 'Third Person Omniscient' }
  ];
  
  const proseStyleOptions = [
    { id: 'minimal', label: 'Minimal' },
    { id: 'balanced', label: 'Balanced' },
    { id: 'descriptive', label: 'Descriptive' }
  ];
  
  const dialogStyleOptions = [
    { id: 'direct', label: 'Direct' },
    { id: 'indirect', label: 'Indirect' },
    { id: 'mixed', label: 'Mixed' }
  ];
  
  const toneOptions = [
    { id: 'dramatic', label: 'Dramatic' },
    { id: 'whimsical', label: 'Whimsical' },
    { id: 'serious', label: 'Serious' },
    { id: 'humorous', label: 'Humorous' },
    { id: 'melancholic', label: 'Melancholic' },
    { id: 'suspenseful', label: 'Suspenseful' }
  ];
  
  const handleChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    const { name, value } = e.target;
    setOptions(prev => ({ ...prev, [name]: value }));
  };
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
        <div className="flex justify-between items-center p-4 border-b">
          <h3 className="text-lg font-medium">Regenerate Section</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <XIcon className="h-5 w-5" />
          </button>
        </div>
        
        <div className="p-4">
          <p className="text-gray-600 mb-4">Adjust the style options for this section:</p>
          
          <div className="space-y-4">
            {/* Narrative Voice */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Narrative Voice
              </label>
              <select
                name="narrativeVoice"
                value={options.narrativeVoice}
                onChange={handleChange}
                className="w-full p-2 border border-gray-300 rounded"
              >
                {narrativeVoiceOptions.map(option => (
                  <option key={option.id} value={option.id}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            
            {/* Prose Style */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Prose Style
              </label>
              <select
                name="proseStyle"
                value={options.proseStyle}
                onChange={handleChange}
                className="w-full p-2 border border-gray-300 rounded"
              >
                {proseStyleOptions.map(option => (
                  <option key={option.id} value={option.id}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            
            {/* Dialog Style */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Dialog Style
              </label>
              <select
                name="dialogStyle"
                value={options.dialogStyle}
                onChange={handleChange}
                className="w-full p-2 border border-gray-300 rounded"
              >
                {dialogStyleOptions.map(option => (
                  <option key={option.id} value={option.id}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            
            {/* Tone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Tone
              </label>
              <select
                name="tonePreference"
                value={options.tonePreference}
                onChange={handleChange}
                className="w-full p-2 border border-gray-300 rounded"
              >
                {toneOptions.map(option => (
                  <option key={option.id} value={option.id}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>
        
        <div className="p-4 border-t bg-gray-50 flex justify-end space-x-2 rounded-b-xl">
          <button
            onClick={onClose}
            className="px-4 py-2 border border-gray-300 rounded text-gray-700 hover:bg-gray-100"
          >
            Cancel
          </button>
          <button
            onClick={() => onRegenerate(options)}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700 flex items-center"
          >
            <RefreshIcon className="h-4 w-4 mr-1" />
            Regenerate
          </button>
        </div>
      </div>
    </div>
  );
};

export default SectionRegenerateDialog;