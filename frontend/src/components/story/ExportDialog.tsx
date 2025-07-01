// src/components/story/ExportDialog.tsx
import React, { useState } from 'react';
import {
  DocumentTextIcon,
  DocumentIcon,
  BookOpenIcon,
  CodeIcon,
  XIcon
} from '@heroicons/react/24/outline';

interface ExportDialogProps {
  onExport: (format: 'pdf' | 'docx' | 'epub' | 'txt') => void;
  onClose: () => void;
}

const ExportDialog: React.FC<ExportDialogProps> = ({ onExport, onClose }) => {
  const [selectedFormat, setSelectedFormat] = useState<'pdf' | 'docx' | 'epub' | 'txt'>('pdf');
  
  const exportFormats = [
    { id: 'pdf', label: 'PDF Document', icon: DocumentTextIcon, description: 'Best for printing or sharing' },
    { id: 'docx', label: 'Word Document', icon: DocumentIcon, description: 'Editable in Microsoft Word' },
    { id: 'epub', label: 'ePub eBook', icon: BookOpenIcon, description: 'For e-readers and mobile devices' },
    { id: 'txt', label: 'Plain Text', icon: CodeIcon, description: 'Simple text format, no formatting' }
  ];
  
  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
      <div className="bg-white rounded-xl shadow-xl max-w-md w-full">
        <div className="flex justify-between items-center p-4 border-b">
          <h3 className="text-lg font-medium">Export Story</h3>
          <button onClick={onClose} className="text-gray-500 hover:text-gray-700">
            <XIcon className="h-5 w-5" />
          </button>
        </div>
        
        <div className="p-4">
          <p className="text-gray-600 mb-4">Select an export format:</p>
          
          <div className="space-y-2">
            {exportFormats.map((format) => (
              <div
                key={format.id}
                className={`flex items-center p-3 border rounded cursor-pointer transition-colors ${
                  selectedFormat === format.id
                    ? 'border-indigo-500 bg-indigo-50'
                    : 'border-gray-200 hover:border-indigo-300'
                }`}
                onClick={() => setSelectedFormat(format.id as any)}
              >
                <format.icon className="h-6 w-6 text-indigo-500 mr-3" />
                <div>
                  <div className="font-medium">{format.label}</div>
                  <div className="text-xs text-gray-500">{format.description}</div>
                </div>
              </div>
            ))}
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
            onClick={() => onExport(selectedFormat)}
            className="px-4 py-2 bg-indigo-600 text-white rounded hover:bg-indigo-700"
          >
            Export
          </button>
        </div>
      </div>
    </div>
  );
};

export default ExportDialog;