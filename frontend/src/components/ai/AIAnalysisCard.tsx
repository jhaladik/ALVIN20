// src/components/ai/AIAnalysisCard.tsx
import React from 'react';
import { AIAnalysis } from '../../types/ai';
import { 
  DocumentDuplicateIcon, 
  ArrowDownTrayIcon,
  StarIcon
} from '@heroicons/react/24/outline';

interface AIAnalysisCardProps {
  analysis: AIAnalysis;
}

const AIAnalysisCard: React.FC<AIAnalysisCardProps> = ({ analysis }) => {
  // Format date for display
  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleString();
  };

  // Copy analysis to clipboard
  const copyToClipboard = () => {
    // Create a text-only version of the analysis without HTML
    const textContent = document.createElement('div');
    textContent.innerHTML = analysis.content;
    navigator.clipboard.writeText(textContent.textContent || textContent.innerText);
    
    // Show a toast or some feedback (would need to implement a toast system)
    alert('Analysis copied to clipboard');
  };

  // Export analysis as markdown
  const exportAsMarkdown = () => {
    // Convert HTML to markdown (this is a simplified version)
    const textContent = document.createElement('div');
    textContent.innerHTML = analysis.content;
    const plainText = textContent.textContent || textContent.innerText;
    
    // Create a title based on critic type and date
    const title = `# ${analysis.criticType.charAt(0).toUpperCase() + analysis.criticType.slice(1)} Analysis\n`;
    const date = `*Generated on ${formatDate(analysis.createdAt)}*\n\n`;
    
    // Create and download the markdown file
    const element = document.createElement('a');
    element.setAttribute('href', 'data:text/markdown;charset=utf-8,' + encodeURIComponent(title + date + plainText));
    element.setAttribute('download', `${analysis.criticType}-analysis-${new Date().toISOString().slice(0, 10)}.md`);
    element.style.display = 'none';
    document.body.appendChild(element);
    element.click();
    document.body.removeChild(element);
  };

  // Render stars for rating if available
  const renderRating = () => {
    if (!analysis.rating) return null;

    return (
      <div className="flex items-center mt-2">
        {[1, 2, 3, 4, 5].map((star) => (
          <StarIcon 
            key={star}
            className={`h-5 w-5 ${
              star <= analysis.rating! 
                ? 'text-yellow-400' 
                : 'text-gray-300'
            }`} 
          />
        ))}
        <span className="ml-2 text-sm text-gray-600">
          {analysis.rating}/5 rating
        </span>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
      {/* Actions toolbar */}
      <div className="bg-gray-50 px-4 py-2 flex justify-between items-center border-b border-gray-200">
        <div>
          <span className="text-xs text-gray-500">
            Generated on {formatDate(analysis.createdAt)}
          </span>
        </div>
        
        <div className="flex space-x-2">
          <button 
            onClick={copyToClipboard}
            className="text-gray-500 hover:text-gray-700 p-1 rounded-md hover:bg-gray-100"
            title="Copy to clipboard"
          >
            <DocumentDuplicateIcon className="h-4 w-4" />
          </button>
          <button 
            onClick={exportAsMarkdown}
            className="text-gray-500 hover:text-gray-700 p-1 rounded-md hover:bg-gray-100"
            title="Export as Markdown"
          >
            <ArrowDownTrayIcon className="h-4 w-4" />
          </button>
        </div>
      </div>
      
      {/* Analysis content */}
      <div className="p-4">
        {renderRating()}
        
        <div 
          className="prose max-w-none mt-3"
          dangerouslySetInnerHTML={{ __html: analysis.content }}
        />
        
        {/* Recommendations section */}
        {analysis.recommendations && analysis.recommendations.length > 0 && (
          <div className="mt-4 pt-4 border-t border-gray-200">
            <h4 className="text-sm font-medium text-gray-900 mb-2">
              Key Recommendations
            </h4>
            <ul className="list-disc list-inside space-y-1 text-sm text-gray-700">
              {analysis.recommendations.map((recommendation, index) => (
                <li key={index}>{recommendation}</li>
              ))}
            </ul>
          </div>
        )}
      </div>
      
      {/* Token usage footer */}
      <div className="px-4 py-2 bg-gray-50 text-xs text-gray-500 border-t border-gray-200">
        Used {analysis.tokenCost} tokens
      </div>
    </div>
  );
};

export default AIAnalysisCard;
