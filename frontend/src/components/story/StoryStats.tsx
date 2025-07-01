// src/components/story/StoryStats.tsx
import React from 'react';
import { StoryStats as StoryStatsType } from '../../types';

interface StoryStatsProps {
  stats: StoryStatsType;
}

const StoryStats: React.FC<StoryStatsProps> = ({ stats }) => {
  const { wordCount, pageCount, readingTime, marketabilityScore, overallQuality } = stats;
  
  return (
    <div className="bg-white rounded-xl shadow-lg p-4">
      <h2 className="text-lg font-semibold mb-3">Story Statistics</h2>
      
      <div className="grid grid-cols-2 md:grid-cols-5 gap-4 text-center">
        <div className="bg-indigo-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-indigo-600">
            {wordCount.toLocaleString()}
          </div>
          <div className="text-sm text-indigo-800">Words</div>
        </div>
        
        <div className="bg-blue-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-blue-600">
            {pageCount}
          </div>
          <div className="text-sm text-blue-800">Pages</div>
        </div>
        
        <div className="bg-green-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-green-600">
            {readingTime}
          </div>
          <div className="text-sm text-green-800">Min Reading</div>
        </div>
        
        <div className="bg-yellow-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-yellow-600">
            {marketabilityScore > 0 ? marketabilityScore.toFixed(1) : 'N/A'}
          </div>
          <div className="text-sm text-yellow-800">Marketability</div>
        </div>
        
        <div className="bg-red-50 p-4 rounded-lg">
          <div className="text-2xl font-bold text-red-600">
            {overallQuality > 0 ? overallQuality.toFixed(1) : 'N/A'}
          </div>
          <div className="text-sm text-red-800">Quality</div>
        </div>
      </div>
    </div>
  );
};

export default StoryStats;