// src/components/analytics/AnalyticsDashboard.tsx - ALVIN Analytics Dashboard
import React, { useState, useEffect } from 'react';
import { 
  LineChart, 
  Line, 
  AreaChart, 
  Area, 
  BarChart, 
  Bar, 
  PieChart, 
  Pie, 
  Cell, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  Legend
} from 'recharts';
import { 
  TrendingUp, 
  TrendingDown, 
  BookOpen, 
  PenTool, 
  Cpu, 
  Calendar,
  Target,
  Award,
  Clock,
  Users,
  Zap,
  BarChart3
} from 'lucide-react';
import { api } from '../../services/api';

interface DashboardStats {
  total_projects: number;
  active_projects: number;
  completed_projects: number;
  total_scenes: number;
  total_words: number;
  tokens_used_week: number;
  tokens_used_month: number;
  ai_operations_week: number;
  writing_streak: number;
  productivity_score: number;
}

interface TokenUsageData {
  date: string;
  tokens_used: number;
  cumulative_tokens: number;
}

interface ProjectProgressData {
  project_name: string;
  progress: number;
  word_count: number;
  target_words: number;
}

interface AIUsageData {
  operation_type: string;
  count: number;
  tokens_used: number;
}

interface WritingActivityData {
  date: string;
  words_written: number;
  scenes_created: number;
  time_spent: number;
}

const COLORS = ['#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6', '#06B6D4'];

const AnalyticsDashboard: React.FC = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [tokenUsage, setTokenUsage] = useState<TokenUsageData[]>([]);
  const [projectProgress, setProjectProgress] = useState<ProjectProgressData[]>([]);
  const [aiUsage, setAiUsage] = useState<AIUsageData[]>([]);
  const [writingActivity, setWritingActivity] = useState<WritingActivityData[]>([]);
  const [timeframe, setTimeframe] = useState<'week' | 'month' | 'quarter'>('month');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadAnalyticsData();
  }, [timeframe]);

  const loadAnalyticsData = async () => {
    setLoading(true);
    try {
      const [
        dashboardResponse,
        tokenResponse,
        progressResponse,
        aiResponse,
        activityResponse
      ] = await Promise.all([
        api.get('/api/analytics/dashboard'),
        api.get(`/api/analytics/token-usage?timeframe=${timeframe}`),
        api.get('/api/analytics/project-progress'),
        api.get(`/api/analytics/ai-usage?timeframe=${timeframe}`),
        api.get(`/api/analytics/writing-activity?timeframe=${timeframe}`)
      ]);

      setStats(dashboardResponse.data);
      setTokenUsage(tokenResponse.data.usage_data || []);
      setProjectProgress(progressResponse.data.projects || []);
      setAiUsage(aiResponse.data.operations || []);
      setWritingActivity(activityResponse.data.activity || []);
    } catch (error) {
      console.error('Failed to load analytics data:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="p-6">
        <div className="animate-pulse space-y-6">
          <div className="h-8 bg-gray-200 rounded w-1/3"></div>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-80 bg-gray-200 rounded-lg"></div>
            ))}
          </div>
        </div>
      </div>
    );
  }

  if (!stats) {
    return (
      <div className="p-6">
        <div className="text-center text-gray-500">
          <BarChart3 className="w-16 h-16 mx-auto mb-4" />
          <p>No analytics data available</p>
        </div>
      </div>
    );
  }

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    change?: number;
    icon: React.ComponentType<any>;
    color: string;
  }> = ({ title, value, change, icon: Icon, color }) => (
    <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
          {change !== undefined && (
            <div className="flex items-center mt-2">
              {change >= 0 ? (
                <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
              ) : (
                <TrendingDown className="w-4 h-4 text-red-500 mr-1" />
              )}
              <span className={`text-sm font-medium ${
                change >= 0 ? 'text-green-600' : 'text-red-600'
              }`}>
                {Math.abs(change)}% from last {timeframe}
              </span>
            </div>
          )}
        </div>
        <div className={`p-3 rounded-full ${color}`}>
          <Icon className="w-6 h-6 text-white" />
        </div>
      </div>
    </div>
  );

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Analytics Dashboard</h1>
          <p className="text-gray-600 mt-2">Track your writing progress and AI usage</p>
        </div>
        <div className="flex items-center space-x-2">
          <select
            value={timeframe}
            onChange={(e) => setTimeframe(e.target.value as 'week' | 'month' | 'quarter')}
            className="px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="week">Last Week</option>
            <option value="month">Last Month</option>
            <option value="quarter">Last Quarter</option>
          </select>
        </div>
      </div>

      {/* Key Stats */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard
          title="Total Projects"
          value={stats.total_projects}
          icon={BookOpen}
          color="bg-blue-500"
        />
        <StatCard
          title="Words Written"
          value={stats.total_words.toLocaleString()}
          icon={PenTool}
          color="bg-green-500"
        />
        <StatCard
          title="AI Operations"
          value={stats.ai_operations_week}
          icon={Cpu}
          color="bg-purple-500"
        />
        <StatCard
          title="Writing Streak"
          value={`${stats.writing_streak} days`}
          icon={Award}
          color="bg-orange-500"
        />
      </div>

      {/* Charts Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Token Usage Chart */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Token Usage Over Time</h3>
          <ResponsiveContainer width="100%" height={300}>
            <AreaChart data={tokenUsage}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Area 
                type="monotone" 
                dataKey="tokens_used" 
                stroke="#3B82F6" 
                fill="#3B82F6" 
                fillOpacity={0.3}
                name="Tokens Used"
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>

        {/* Project Progress */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Project Progress</h3>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={projectProgress} layout="horizontal">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" domain={[0, 100]} />
              <YAxis dataKey="project_name" type="category" width={80} />
              <Tooltip formatter={(value) => [`${value}%`, 'Progress']} />
              <Bar dataKey="progress" fill="#10B981" />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* AI Usage Breakdown */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Operations Breakdown</h3>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={aiUsage}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ operation_type, percent }) => 
                  `${operation_type.replace(/_/g, ' ')} ${(percent * 100).toFixed(0)}%`
                }
                outerRadius={80}
                fill="#8884d8"
                dataKey="count"
              >
                {aiUsage.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Writing Activity */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Daily Writing Activity</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={writingActivity}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line 
                type="monotone" 
                dataKey="words_written" 
                stroke="#3B82F6" 
                strokeWidth={2}
                name="Words Written"
              />
              <Line 
                type="monotone" 
                dataKey="scenes_created" 
                stroke="#10B981" 
                strokeWidth={2}
                name="Scenes Created"
              />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Metrics */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        
        {/* Productivity Insights */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Productivity Insights</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Productivity Score</span>
              <div className="flex items-center">
                <div className="w-16 bg-gray-200 rounded-full h-2 mr-2">
                  <div 
                    className="bg-blue-500 h-2 rounded-full" 
                    style={{ width: `${stats.productivity_score}%` }}
                  ></div>
                </div>
                <span className="font-medium">{stats.productivity_score}%</span>
              </div>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Active Projects</span>
              <span className="font-medium">{stats.active_projects}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Completion Rate</span>
              <span className="font-medium">
                {stats.total_projects > 0 
                  ? Math.round((stats.completed_projects / stats.total_projects) * 100)
                  : 0}%
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Avg. Words/Project</span>
              <span className="font-medium">
                {stats.total_projects > 0 
                  ? Math.round(stats.total_words / stats.total_projects).toLocaleString()
                  : 0}
              </span>
            </div>
          </div>
        </div>

        {/* Token Usage Summary */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Token Usage Summary</h3>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-gray-600">This Week</span>
              <span className="font-medium">{stats.tokens_used_week.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">This Month</span>
              <span className="font-medium">{stats.tokens_used_month.toLocaleString()}</span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">Daily Average</span>
              <span className="font-medium">
                {Math.round(stats.tokens_used_week / 7).toLocaleString()}
              </span>
            </div>
            <div className="flex items-center justify-between">
              <span className="text-gray-600">AI Operations</span>
              <span className="font-medium">{stats.ai_operations_week}</span>
            </div>
          </div>
        </div>

        {/* Writing Goals */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Writing Goals</h3>
          <div className="space-y-4">
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-600">Daily Goal</span>
                <span className="font-medium">500 words</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-green-500 h-2 rounded-full" 
                  style={{ width: '75%' }}
                ></div>
              </div>
              <span className="text-sm text-gray-500">375 / 500 words today</span>
            </div>
            
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-600">Weekly Goal</span>
                <span className="font-medium">3,500 words</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full" 
                  style={{ width: '60%' }}
                ></div>
              </div>
              <span className="text-sm text-gray-500">2,100 / 3,500 words this week</span>
            </div>

            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-gray-600">Monthly Goal</span>
                <span className="font-medium">15,000 words</span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className="bg-purple-500 h-2 rounded-full" 
                  style={{ width: `${Math.min((stats.total_words / 15000) * 100, 100)}%` }}
                ></div>
              </div>
              <span className="text-sm text-gray-500">
                {stats.total_words.toLocaleString()} / 15,000 words this month
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Recent Activity Feed */}
      <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-200">
        <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
        <div className="space-y-4">
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center">
              <PenTool className="w-4 h-4 text-blue-600" />
            </div>
            <div>
              <p className="font-medium">Created new scene "The Discovery"</p>
              <p className="text-sm text-gray-500">2 hours ago</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-green-100 rounded-full flex items-center justify-center">
              <Cpu className="w-4 h-4 text-green-600" />
            </div>
            <div>
              <p className="font-medium">AI analysis completed for "Chapter 3"</p>
              <p className="text-sm text-gray-500">4 hours ago</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-purple-100 rounded-full flex items-center justify-center">
              <Target className="w-4 h-4 text-purple-600" />
            </div>
            <div>
              <p className="font-medium">Achieved daily writing goal</p>
              <p className="text-sm text-gray-500">Yesterday</p>
            </div>
          </div>
          <div className="flex items-center space-x-3">
            <div className="w-8 h-8 bg-orange-100 rounded-full flex items-center justify-center">
              <BookOpen className="w-4 h-4 text-orange-600" />
            </div>
            <div>
              <p className="font-medium">Started new project "Mystery Novel"</p>
              <p className="text-sm text-gray-500">3 days ago</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AnalyticsDashboard;