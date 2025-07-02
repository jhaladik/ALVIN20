// frontend/src/pages/Analytics.tsx - Complete Analytics Dashboard Implementation
import React, { useState, useEffect } from 'react';
import { api } from '../services/api';
import { useAuth } from '../hooks/useAuth';
import LoadingSpinner from '../components/ui/LoadingSpinner';
import {
  ChartBarIcon,
  DocumentTextIcon,
  ClockIcon,
  CpuChipIcon,
  TrendingUpIcon,
  UserGroupIcon
} from '@heroicons/react/24/outline';

interface AnalyticsData {
  overview: {
    total_projects: number;
    active_projects: number;
    completed_projects: number;
    total_scenes: number;
    total_word_count: number;
    tokens_used: number;
    tokens_remaining: number;
    tokens_limit: number;
  };
  recent_activity: {
    tokens_this_week: number;
    tokens_this_month: number;
    ai_operations_this_week: number;
    recent_projects: any[];
  };
  ai_usage: {
    top_operations: Array<{
      operation_type: string;
      count: number;
      total_cost: number;
      avg_cost: number;
    }>;
  };
  productivity: {
    daily_activity: Array<{
      date: string;
      scenes_created: number;
      words_written: number;
    }>;
    monthly_trend: Array<{
      date: string;
      scenes_created: number;
      words_written: number;
    }>;
  };
  distributions: {
    genres: Array<{ genre: string; count: number }>;
    phases: Array<{ phase: string; count: number }>;
  };
}

const Analytics: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const { user } = useAuth();

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      const response = await api.get('/api/analytics/dashboard');
      setData(response.data);
      setError('');
    } catch (err: any) {
      setError(err.response?.data?.message || 'Failed to load analytics');
      console.error('Analytics fetch error:', err);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex h-64 items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  if (error) {
    return (
      <div className="rounded-md bg-red-50 p-4">
        <div className="text-sm text-red-700">
          <strong>Error loading analytics:</strong> {error}
          <button 
            onClick={fetchAnalytics}
            className="ml-4 text-red-600 hover:text-red-500 underline"
          >
            Try Again
          </button>
        </div>
      </div>
    );
  }

  if (!data) {
    return (
      <div className="text-center py-12">
        <p className="text-gray-500">No analytics data available</p>
      </div>
    );
  }

  const { overview, recent_activity, ai_usage, productivity, distributions } = data;

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="border-b border-gray-200 pb-4">
        <h1 className="text-2xl font-bold text-gray-900">Analytics Dashboard</h1>
        <p className="text-gray-600">Track your writing progress and AI usage</p>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <OverviewCard
          title="Total Projects"
          value={overview.total_projects}
          icon={DocumentTextIcon}
          subtitle={`${overview.active_projects} active`}
          color="blue"
        />
        <OverviewCard
          title="Total Scenes"
          value={overview.total_scenes}
          icon={ChartBarIcon}
          subtitle="Across all projects"
          color="green"
        />
        <OverviewCard
          title="Words Written"
          value={overview.total_word_count.toLocaleString()}
          icon={TrendingUpIcon}
          subtitle="Total word count"
          color="purple"
        />
        <OverviewCard
          title="AI Tokens Used"
          value={overview.tokens_used}
          icon={CpuChipIcon}
          subtitle={`${overview.tokens_remaining} remaining`}
          color="orange"
        />
      </div>

      {/* Recent Activity & AI Usage */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Tokens this week</span>
              <span className="font-medium">{recent_activity.tokens_this_week}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">Tokens this month</span>
              <span className="font-medium">{recent_activity.tokens_this_month}</span>
            </div>
            <div className="flex justify-between items-center">
              <span className="text-sm text-gray-600">AI operations this week</span>
              <span className="font-medium">{recent_activity.ai_operations_this_week}</span>
            </div>
          </div>

          {recent_activity.recent_projects.length > 0 && (
            <div className="mt-6">
              <h4 className="text-sm font-medium text-gray-900 mb-2">Recent Projects</h4>
              <div className="space-y-2">
                {recent_activity.recent_projects.slice(0, 3).map((project: any) => (
                  <div key={project.id} className="flex justify-between items-center text-sm">
                    <span className="text-gray-600 truncate">{project.title}</span>
                    <span className="text-gray-400">
                      {new Date(project.updated_at).toLocaleDateString()}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* AI Usage */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Top AI Operations</h3>
          {ai_usage.top_operations.length > 0 ? (
            <div className="space-y-3">
              {ai_usage.top_operations.map((operation, index) => (
                <div key={index} className="flex justify-between items-center">
                  <div>
                    <span className="text-sm font-medium text-gray-900">
                      {operation.operation_type.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                    </span>
                    <div className="text-xs text-gray-500">
                      {operation.count} operations • Avg cost: {operation.avg_cost.toFixed(2)}
                    </div>
                  </div>
                  <span className="text-sm font-medium">{operation.total_cost.toFixed(2)}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No AI operations yet</p>
          )}
        </div>
      </div>

      {/* Productivity Chart */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Writing Productivity (Last 7 Days)</h3>
        <div className="h-64 flex items-end space-x-2">
          {productivity.daily_activity.slice(0, 7).reverse().map((day, index) => {
            const maxWords = Math.max(...productivity.daily_activity.slice(0, 7).map(d => d.words_written));
            const height = maxWords > 0 ? (day.words_written / maxWords) * 100 : 0;
            
            return (
              <div key={index} className="flex-1 flex flex-col items-center">
                <div 
                  className="w-full bg-blue-500 rounded-t-sm min-h-[4px]"
                  style={{ height: `${Math.max(height, 2)}%` }}
                  title={`${day.words_written} words, ${day.scenes_created} scenes`}
                />
                <div className="text-xs text-gray-500 mt-2 transform -rotate-45 origin-top-left">
                  {new Date(day.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                </div>
              </div>
            );
          })}
        </div>
        <div className="mt-4 text-sm text-gray-600 text-center">
          Hover over bars to see details
        </div>
      </div>

      {/* Genre & Phase Distribution */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Genre Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Project Genres</h3>
          {distributions.genres.length > 0 ? (
            <div className="space-y-3">
              {distributions.genres.map((genre, index) => {
                const maxCount = Math.max(...distributions.genres.map(g => g.count));
                const percentage = (genre.count / maxCount) * 100;
                
                return (
                  <div key={index} className="flex items-center">
                    <div className="w-24 text-sm text-gray-600 capitalize">{genre.genre}</div>
                    <div className="flex-1 mx-3">
                      <div className="bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-purple-500 h-2 rounded-full"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                    <div className="text-sm font-medium">{genre.count}</div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No projects yet</p>
          )}
        </div>

        {/* Phase Distribution */}
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Project Phases</h3>
          {distributions.phases.length > 0 ? (
            <div className="space-y-3">
              {distributions.phases.map((phase, index) => {
                const maxCount = Math.max(...distributions.phases.map(p => p.count));
                const percentage = (phase.count / maxCount) * 100;
                
                return (
                  <div key={index} className="flex items-center">
                    <div className="w-24 text-sm text-gray-600 capitalize">{phase.phase}</div>
                    <div className="flex-1 mx-3">
                      <div className="bg-gray-200 rounded-full h-2">
                        <div 
                          className="bg-green-500 h-2 rounded-full"
                          style={{ width: `${percentage}%` }}
                        />
                      </div>
                    </div>
                    <div className="text-sm font-medium">{phase.count}</div>
                  </div>
                );
              })}
            </div>
          ) : (
            <p className="text-sm text-gray-500">No projects yet</p>
          )}
        </div>
      </div>

      {/* Token Usage Progress */}
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-medium text-gray-900 mb-4">Token Usage</h3>
        <div className="flex items-center justify-between mb-2">
          <span className="text-sm text-gray-600">Used: {overview.tokens_used}</span>
          <span className="text-sm text-gray-600">Limit: {overview.tokens_limit}</span>
        </div>
        <div className="bg-gray-200 rounded-full h-3">
          <div 
            className={`h-3 rounded-full ${
              (overview.tokens_used / overview.tokens_limit) > 0.8 
                ? 'bg-red-500' 
                : (overview.tokens_used / overview.tokens_limit) > 0.6 
                  ? 'bg-yellow-500' 
                  : 'bg-green-500'
            }`}
            style={{ width: `${Math.min((overview.tokens_used / overview.tokens_limit) * 100, 100)}%` }}
          />
        </div>
        <div className="mt-2 text-sm text-gray-600">
          {overview.tokens_remaining} tokens remaining ({Math.round((overview.tokens_remaining / overview.tokens_limit) * 100)}%)
        </div>
      </div>
    </div>
  );
};

// Overview Card Component
interface OverviewCardProps {
  title: string;
  value: string | number;
  icon: React.ComponentType<{ className?: string }>;
  subtitle?: string;
  color: 'blue' | 'green' | 'purple' | 'orange';
}

const OverviewCard: React.FC<OverviewCardProps> = ({ 
  title, 
  value, 
  icon: Icon, 
  subtitle, 
  color 
}) => {
  const colorClasses = {
    blue: 'bg-blue-500 text-blue-100',
    green: 'bg-green-500 text-green-100', 
    purple: 'bg-purple-500 text-purple-100',
    orange: 'bg-orange-500 text-orange-100'
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <div className="flex items-center">
        <div className={`flex-shrink-0 p-3 rounded-md ${colorClasses[color]}`}>
          <Icon className="h-6 w-6" />
        </div>
        <div className="ml-4">
          <h3 className="text-sm font-medium text-gray-900">{title}</h3>
          <p className="text-2xl font-bold text-gray-900">{value}</p>
          {subtitle && (
            <p className="text-sm text-gray-500">{subtitle}</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Analytics;