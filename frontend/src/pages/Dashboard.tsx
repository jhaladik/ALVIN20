// src/pages/Dashboard.tsx - Enhanced ALVIN Dashboard with Analytics
import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { api } from '../services/api';
import AnalyticsDashboard from '../components/analytics/AnalyticsDashboard';
import {
  Plus,
  BookOpen,
  PenTool,
  Cpu,
  TrendingUp,
  Calendar,
  Target,
  Award,
  Clock,
  Users,
  BarChart3,
  Activity,
  Zap,
  AlertCircle,
  CheckCircle,
  ArrowRight,
  Filter,
  Search,
  MoreVertical,
  Play,
  Pause,
  Eye,
  Edit3
} from 'lucide-react';

interface Project {
  id: string;
  title: string;
  description: string;
  genre: string;
  current_phase: 'idea' | 'expand' | 'story';
  status: 'active' | 'paused' | 'completed' | 'archived';
  current_word_count: number;
  target_word_count: number;
  updated_at: string;
  created_at: string;
}

interface DashboardStats {
  total_projects: number;
  active_projects: number;
  completed_projects: number;
  total_words: number;
  tokens_used_week: number;
  tokens_remaining: number;
  writing_streak: number;
  productivity_score: number;
}

interface RecentActivity {
  id: string;
  type: 'project_created' | 'scene_added' | 'ai_analysis' | 'goal_achieved';
  description: string;
  timestamp: string;
  project_title?: string;
}

const Dashboard: React.FC = () => {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<'overview' | 'analytics'>('overview');
  const [projects, setProjects] = useState<Project[]>([]);
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [recentActivity, setRecentActivity] = useState<RecentActivity[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    setLoading(true);
    try {
      const [projectsRes, statsRes, activityRes] = await Promise.all([
        api.get('/api/projects?limit=10&sort=updated_at&order=desc'),
        api.get('/api/analytics/dashboard'),
        api.get('/api/analytics/recent-activity?limit=10')
      ]);

      setProjects(projectsRes.data.projects || []);
      setStats(statsRes.data);
      setRecentActivity(activityRes.data.activities || []);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
    } finally {
      setLoading(false);
    }
  };

  const filteredProjects = projects.filter(project => {
    const matchesSearch = project.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         project.description.toLowerCase().includes(searchTerm.toLowerCase());
    const matchesStatus = statusFilter === 'all' || project.status === statusFilter;
    return matchesSearch && matchesStatus;
  });

  const getPhaseColor = (phase: string) => {
    switch (phase) {
      case 'idea': return 'bg-yellow-100 text-yellow-800';
      case 'expand': return 'bg-blue-100 text-blue-800';
      case 'story': return 'bg-green-100 text-green-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'active': return 'bg-green-100 text-green-800';
      case 'paused': return 'bg-yellow-100 text-yellow-800';
      case 'completed': return 'bg-blue-100 text-blue-800';
      case 'archived': return 'bg-gray-100 text-gray-800';
      default: return 'bg-gray-100 text-gray-800';
    }
  };

  const getProgressPercentage = (current: number, target: number) => {
    if (!target) return 0;
    return Math.min((current / target) * 100, 100);
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
    
    if (diffInMinutes < 60) return `${diffInMinutes}m ago`;
    if (diffInMinutes < 1440) return `${Math.floor(diffInMinutes / 60)}h ago`;
    return `${Math.floor(diffInMinutes / 1440)}d ago`;
  };

  const StatCard: React.FC<{
    title: string;
    value: string | number;
    change?: number;
    icon: React.ComponentType<any>;
    color: string;
    action?: () => void;
  }> = ({ title, value, change, icon: Icon, color, action }) => (
    <div 
      className={`bg-white p-6 rounded-lg shadow-sm border border-gray-200 ${action ? 'cursor-pointer hover:shadow-md transition-shadow' : ''}`}
      onClick={action}
    >
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm font-medium text-gray-600">{title}</p>
          <p className="text-2xl font-bold text-gray-900 mt-2">{value}</p>
          {change !== undefined && (
            <div className="flex items-center mt-2">
              <TrendingUp className={`w-4 h-4 mr-1 ${change >= 0 ? 'text-green-500' : 'text-red-500'}`} />
              <span className={`text-sm font-medium ${change >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                {Math.abs(change)}% from last week
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

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 p-6">
        <div className="max-w-7xl mx-auto">
          <div className="animate-pulse space-y-6">
            <div className="h-8 bg-gray-200 rounded w-1/3"></div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              {[...Array(4)].map((_, i) => (
                <div key={i} className="h-32 bg-gray-200 rounded-lg"></div>
              ))}
            </div>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              <div className="lg:col-span-2 h-96 bg-gray-200 rounded-lg"></div>
              <div className="h-96 bg-gray-200 rounded-lg"></div>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">
              Welcome back, {user?.username}! 👋
            </h1>
            <p className="text-gray-600 mt-2">Here's what's happening with your writing today</p>
          </div>
          <div className="flex items-center space-x-3">
            <div className="flex bg-gray-100 rounded-lg p-1">
              <button
                onClick={() => setActiveTab('overview')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'overview'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <Activity className="w-4 h-4 mr-2 inline" />
                Overview
              </button>
              <button
                onClick={() => setActiveTab('analytics')}
                className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                  activeTab === 'analytics'
                    ? 'bg-white text-gray-900 shadow-sm'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                <BarChart3 className="w-4 h-4 mr-2 inline" />
                Analytics
              </button>
            </div>
            <Link
              to="/projects"
              className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
            >
              <Plus className="w-4 h-4 mr-2" />
              New Project
            </Link>
          </div>
        </div>

        {activeTab === 'overview' && (
          <>
            {/* Stats Cards */}
            {stats && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
                <StatCard
                  title="Total Projects"
                  value={stats.total_projects}
                  icon={BookOpen}
                  color="bg-blue-500"
                  action={() => window.location.href = '/projects'}
                />
                <StatCard
                  title="Words Written"
                  value={stats.total_words.toLocaleString()}
                  change={12}
                  icon={PenTool}
                  color="bg-green-500"
                />
                <StatCard
                  title="Tokens Used"
                  value={stats.tokens_used_week}
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
            )}

            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Recent Projects */}
              <div className="lg:col-span-2 bg-white rounded-lg shadow-sm border border-gray-200">
                <div className="p-6 border-b border-gray-200">
                  <div className="flex items-center justify-between">
                    <h2 className="text-lg font-semibold text-gray-900">Recent Projects</h2>
                    <div className="flex items-center space-x-2">
                      <div className="relative">
                        <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400" />
                        <input
                          type="text"
                          placeholder="Search projects..."
                          value={searchTerm}
                          onChange={(e) => setSearchTerm(e.target.value)}
                          className="pl-9 pr-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                      </div>
                      <select
                        value={statusFilter}
                        onChange={(e) => setStatusFilter(e.target.value)}
                        className="px-3 py-1.5 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
                      >
                        <option value="all">All Status</option>
                        <option value="active">Active</option>
                        <option value="paused">Paused</option>
                        <option value="completed">Completed</option>
                      </select>
                    </div>
                  </div>
                </div>

                <div className="p-6">
                  {filteredProjects.length === 0 ? (
                    <div className="text-center py-12">
                      <BookOpen className="w-12 h-12 text-gray-400 mx-auto mb-4" />
                      <h3 className="text-lg font-medium text-gray-900 mb-2">No projects found</h3>
                      <p className="text-gray-500 mb-4">
                        {searchTerm || statusFilter !== 'all' 
                          ? 'Try adjusting your filters'
                          : 'Start your writing journey by creating your first project'
                        }
                      </p>
                      <Link
                        to="/projects"
                        className="inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                      >
                        <Plus className="w-4 h-4 mr-2" />
                        Create Project
                      </Link>
                    </div>
                  ) : (
                    <div className="space-y-4">
                      {filteredProjects.map((project) => (
                        <div key={project.id} className="border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow">
                          <div className="flex items-start justify-between">
                            <div className="flex-1">
                              <div className="flex items-center space-x-2 mb-2">
                                <h3 className="font-medium text-gray-900">{project.title}</h3>
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getPhaseColor(project.current_phase)}`}>
                                  {project.current_phase}
                                </span>
                                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusColor(project.status)}`}>
                                  {project.status}
                                </span>
                              </div>
                              <p className="text-sm text-gray-600 mb-3">{project.description}</p>
                              
                              {/* Progress Bar */}
                              {project.target_word_count > 0 && (
                                <div className="mb-3">
                                  <div className="flex items-center justify-between text-xs text-gray-500 mb-1">
                                    <span>Progress</span>
                                    <span>{project.current_word_count.toLocaleString()} / {project.target_word_count.toLocaleString()} words</span>
                                  </div>
                                  <div className="w-full bg-gray-200 rounded-full h-2">
                                    <div
                                      className="bg-blue-500 h-2 rounded-full transition-all duration-300"
                                      style={{ width: `${getProgressPercentage(project.current_word_count, project.target_word_count)}%` }}
                                    ></div>
                                  </div>
                                </div>
                              )}
                              
                              <div className="flex items-center text-xs text-gray-500">
                                <Calendar className="w-3 h-3 mr-1" />
                                Updated {formatTimeAgo(project.updated_at)}
                                {project.genre && (
                                  <>
                                    <span className="mx-2">•</span>
                                    <span>{project.genre}</span>
                                  </>
                                )}
                              </div>
                            </div>
                            
                            <div className="flex items-center space-x-2 ml-4">
                              <Link
                                to={`/projects/${project.id}`}
                                className="p-2 text-gray-400 hover:text-blue-600 transition-colors"
                                title="View project"
                              >
                                <Eye className="w-4 h-4" />
                              </Link>
                              <Link
                                to={`/projects/${project.id}/scenes`}
                                className="p-2 text-gray-400 hover:text-green-600 transition-colors"
                                title="Edit scenes"
                              >
                                <Edit3 className="w-4 h-4" />
                              </Link>
                              <button className="p-2 text-gray-400 hover:text-gray-600 transition-colors">
                                <MoreVertical className="w-4 h-4" />
                              </button>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {filteredProjects.length > 0 && (
                    <div className="mt-6 text-center">
                      <Link
                        to="/projects"
                        className="inline-flex items-center text-sm text-blue-600 hover:text-blue-700"
                      >
                        View all projects
                        <ArrowRight className="w-4 h-4 ml-1" />
                      </Link>
                    </div>
                  )}
                </div>
              </div>

              {/* Recent Activity & Quick Actions */}
              <div className="space-y-6">
                {/* Quick Actions */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Actions</h3>
                  <div className="space-y-3">
                    <Link
                      to="/projects"
                      className="flex items-center p-3 rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-colors"
                    >
                      <Plus className="w-5 h-5 text-blue-600 mr-3" />
                      <span className="font-medium text-gray-900">Create New Project</span>
                    </Link>
                    <Link
                      to="/ai-workshop"
                      className="flex items-center p-3 rounded-lg border border-gray-200 hover:border-purple-300 hover:bg-purple-50 transition-colors"
                    >
                      <Zap className="w-5 h-5 text-purple-600 mr-3" />
                      <span className="font-medium text-gray-900">AI Workshop</span>
                    </Link>
                    <Link
                      to="/collaboration"
                      className="flex items-center p-3 rounded-lg border border-gray-200 hover:border-green-300 hover:bg-green-50 transition-colors"
                    >
                      <Users className="w-5 h-5 text-green-600 mr-3" />
                      <span className="font-medium text-gray-900">Collaborate</span>
                    </Link>
                  </div>
                </div>

                {/* Recent Activity */}
                <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                  <h3 className="text-lg font-semibold text-gray-900 mb-4">Recent Activity</h3>
                  <div className="space-y-3">
                    {recentActivity.length === 0 ? (
                      <p className="text-gray-500 text-sm">No recent activity</p>
                    ) : (
                      recentActivity.map((activity) => (
                        <div key={activity.id} className="flex items-start space-x-3">
                          <div className="w-8 h-8 bg-blue-100 rounded-full flex items-center justify-center flex-shrink-0">
                            {activity.type === 'project_created' && <BookOpen className="w-4 h-4 text-blue-600" />}
                            {activity.type === 'scene_added' && <PenTool className="w-4 h-4 text-green-600" />}
                            {activity.type === 'ai_analysis' && <Cpu className="w-4 h-4 text-purple-600" />}
                            {activity.type === 'goal_achieved' && <Target className="w-4 h-4 text-orange-600" />}
                          </div>
                          <div className="flex-1 min-w-0">
                            <p className="text-sm text-gray-900">{activity.description}</p>
                            <p className="text-xs text-gray-500">{formatTimeAgo(activity.timestamp)}</p>
                          </div>
                        </div>
                      ))
                    )}
                  </div>
                </div>

                {/* Writing Goals */}
                {stats && (
                  <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
                    <h3 className="text-lg font-semibold text-gray-900 mb-4">Today's Goals</h3>
                    <div className="space-y-4">
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-700">Daily Writing</span>
                          <span className="text-sm text-gray-500">375 / 500 words</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-green-500 h-2 rounded-full" style={{ width: '75%' }}></div>
                        </div>
                      </div>
                      
                      <div>
                        <div className="flex items-center justify-between mb-2">
                          <span className="text-sm font-medium text-gray-700">Weekly Target</span>
                          <span className="text-sm text-gray-500">2,100 / 3,500 words</span>
                        </div>
                        <div className="w-full bg-gray-200 rounded-full h-2">
                          <div className="bg-blue-500 h-2 rounded-full" style={{ width: '60%' }}></div>
                        </div>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </>
        )}

        {activeTab === 'analytics' && <AnalyticsDashboard />}
      </div>
    </div>
  );
};

export default Dashboard;