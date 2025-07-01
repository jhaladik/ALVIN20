// src/components/story/StoryStyleSelector.tsx
import React, { useState } from 'react';
import { ChevronDownIcon } from '@heroicons/react/24/outline';
import { NarrativeOptions } from '../../types';

interface StoryStyleSelectorProps {
  options: NarrativeOptions;
  onChange: (options: Partial<NarrativeOptions>) => void;
  disabled?: boolean;
}

const StoryStyleSelector: React.FC<StoryStyleSelectorProps> = ({
  options,
  onChange,
  disabled = false
}) => {
  const [isOpen, setIsOpen] = useState(false);
  
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
  
  return (
    <div className="relative">
      <button
        type="button"
        className={`flex items-center gap-1 px-2 py-1 text-sm rounded border ${
          disabled 
            ? 'border-gray-200 text-gray-400 bg-gray-50' 
            : 'border-gray-300 text-gray-700 hover:bg-gray-50'
        }`}
        onClick={() => setIsOpen(!isOpen)}
        disabled={disabled}
      >
        <span>Narrative Style</span>
        <ChevronDownIcon className="h-4 w-4" />
      </button>
      
      {isOpen && (
        <div className="absolute top-full left-0 mt-1 w-64 bg-white rounded-md shadow-lg z-10 p-2">
          <div className="text-xs font-medium text-gray-500 mb-2 pb-1 border-b">
            Narrative Style Options
          </div>
          
          {/* Narrative Voice */}
          <div className="mb-3">
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Narrative Voice
            </label>
            <select
              value={options.narrativeVoice}
              onChange={(e) => onChange({ narrativeVoice: e.target.value as any })}
              className="w-full text-sm rounded border border-gray-300 p-1"
            >
              {narrativeVoiceOptions.map(option => (
                <option key={option.id} value={option.id}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          {/* Prose Style */}
          <div className="mb-3">
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Prose Style
            </label>
            <select
              value={options.proseStyle}
              onChange={(e) => onChange({ proseStyle: e.target.value as any })}
              className="w-full text-sm rounded border border-gray-300 p-1"
            >
              {proseStyleOptions.map(option => (
                <option key={option.id} value={option.id}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          {/* Dialog Style */}
          <div className="mb-3">
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Dialog Style
            </label>
            <select
              value={options.dialogStyle}
              onChange={(e) => onChange({ dialogStyle: e.target.value as any })}
              className="w-full text-sm rounded border border-gray-300 p-1"
            >
              {dialogStyleOptions.map(option => (
                <option key={option.id} value={option.id}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          {/* Tone */}
          <div className="mb-2">
            <label className="block text-xs font-medium text-gray-700 mb-1">
              Tone
            </label>
            <select
              value={options.tonePreference}
              onChange={(e) => onChange({ tonePreference: e.target.value })}
              className="w-full text-sm rounded border border-gray-300 p-1"
            >
              {toneOptions.map(option => (
                <option key={option.id} value={option.id}>
                  {option.label}
                </option>
              ))}
            </select>
          </div>
          
          <div className="pt-2 border-t flex justify-end">
            <button
              type="button"
              className="text-xs text-indigo-600 hover:text-indigo-800"
              onClick={() => setIsOpen(false)}
            >
              Close
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default StoryStyleSelector;