// src/pages/Settings.tsx - Complete ALVIN Settings Page
import React, { useState, useEffect } from 'react';
import { useAuth } from '../hooks/useAuth';
import { api } from '../services/api';
import { 
  User, 
  Lock, 
  CreditCard, 
  Bell, 
  Users, 
  Download, 
  Upload, 
  Key, 
  Trash2,
  Eye,
  EyeOff,
  Save,
  AlertTriangle,
  CheckCircle,
  X
} from 'lucide-react';

interface UserProfile {
  username: string;
  email: string;
  full_name: string;
  bio: string;
  avatar_url: string;
}

interface BillingInfo {
  plan: string;
  tokens_used: number;
  tokens_limit: number;
  subscription_status: string;
  next_billing_date?: string;
}

interface NotificationSettings {
  email_notifications: boolean;
  collaboration_updates: boolean;
  ai_task_completion: boolean;
  billing_alerts: boolean;
  security_alerts: boolean;
}

const Settings: React.FC = () => {
  const { user, logout } = useAuth();
  const [activeTab, setActiveTab] = useState('profile');
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState<{ type: 'success' | 'error', text: string } | null>(null);
  
  // Profile state
  const [profile, setProfile] = useState<UserProfile>({
    username: '',
    email: '',
    full_name: '',
    bio: '',
    avatar_url: ''
  });
  
  // Password change state
  const [passwordData, setPasswordData] = useState({
    current_password: '',
    new_password: '',
    confirm_password: ''
  });
  const [showPasswords, setShowPasswords] = useState({
    current: false,
    new: false,
    confirm: false
  });
  
  // Billing state
  const [billingInfo, setBillingInfo] = useState<BillingInfo | null>(null);
  
  // Notifications state
  const [notifications, setNotifications] = useState<NotificationSettings>({
    email_notifications: true,
    collaboration_updates: true,
    ai_task_completion: true,
    billing_alerts: true,
    security_alerts: true
  });
  
  // API Key state
  const [apiKeys, setApiKeys] = useState<Array<{id: string, name: string, created_at: string, last_used?: string}>>([]);
  const [showNewKeyForm, setShowNewKeyForm] = useState(false);
  const [newKeyName, setNewKeyName] = useState('');
  
  // Account deletion state
  const [showDeleteAccount, setShowDeleteAccount] = useState(false);
  const [deleteConfirmation, setDeleteConfirmation] = useState('');

  useEffect(() => {
    loadUserData();
    loadBillingInfo();
    loadNotificationSettings();
    loadApiKeys();
  }, []);

  const loadUserData = async () => {
    try {
      const response = await api.get('/api/auth/me');
      const userData = response.data.user;
      setProfile({
        username: userData.username || '',
        email: userData.email || '',
        full_name: userData.full_name || '',
        bio: userData.bio || '',
        avatar_url: userData.avatar_url || ''
      });
    } catch (error) {
      showMessage('error', 'Failed to load user data');
    }
  };

  const loadBillingInfo = async () => {
    try {
      const response = await api.get('/api/billing/subscription');
      setBillingInfo(response.data);
    } catch (error) {
      console.error('Failed to load billing info:', error);
    }
  };

  const loadNotificationSettings = async () => {
    try {
      const response = await api.get('/api/auth/notification-preferences');
      setNotifications(response.data);
    } catch (error) {
      console.error('Failed to load notification settings:', error);
    }
  };

  const loadApiKeys = async () => {
    try {
      const response = await api.get('/api/auth/api-keys');
      setApiKeys(response.data.keys);
    } catch (error) {
      console.error('Failed to load API keys:', error);
    }
  };

  const showMessage = (type: 'success' | 'error', text: string) => {
    setMessage({ type, text });
    setTimeout(() => setMessage(null), 5000);
  };

  const updateProfile = async () => {
    setLoading(true);
    try {
      await api.put('/api/auth/profile', profile);
      showMessage('success', 'Profile updated successfully');
    } catch (error: any) {
      showMessage('error', error.response?.data?.message || 'Failed to update profile');
    } finally {
      setLoading(false);
    }
  };

  const changePassword = async () => {
    if (passwordData.new_password !== passwordData.confirm_password) {
      showMessage('error', 'New passwords do not match');
      return;
    }
    
    if (passwordData.new_password.length < 6) {
      showMessage('error', 'Password must be at least 6 characters');
      return;
    }

    setLoading(true);
    try {
      await api.post('/api/auth/change-password', {
        current_password: passwordData.current_password,
        new_password: passwordData.new_password
      });
      setPasswordData({ current_password: '', new_password: '', confirm_password: '' });
      showMessage('success', 'Password changed successfully');
    } catch (error: any) {
      showMessage('error', error.response?.data?.message || 'Failed to change password');
    } finally {
      setLoading(false);
    }
  };

  const updateNotifications = async () => {
    setLoading(true);
    try {
      await api.put('/api/auth/notification-preferences', notifications);
      showMessage('success', 'Notification preferences updated');
    } catch (error: any) {
      showMessage('error', error.response?.data?.message || 'Failed to update preferences');
    } finally {
      setLoading(false);
    }
  };

  const createApiKey = async () => {
    if (!newKeyName.trim()) {
      showMessage('error', 'Please enter a name for the API key');
      return;
    }

    setLoading(true);
    try {
      const response = await api.post('/api/auth/api-keys', { name: newKeyName });
      await loadApiKeys();
      setNewKeyName('');
      setShowNewKeyForm(false);
      showMessage('success', `API key created: ${response.data.key}`);
    } catch (error: any) {
      showMessage('error', error.response?.data?.message || 'Failed to create API key');
    } finally {
      setLoading(false);
    }
  };

  const revokeApiKey = async (keyId: string) => {
    if (!confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
      return;
    }

    try {
      await api.delete(`/api/auth/api-keys/${keyId}`);
      await loadApiKeys();
      showMessage('success', 'API key revoked');
    } catch (error: any) {
      showMessage('error', error.response?.data?.message || 'Failed to revoke API key');
    }
  };

  const exportData = async () => {
    try {
      const response = await api.get('/api/auth/export-data', { responseType: 'blob' });
      const blob = new Blob([response.data], { type: 'application/json' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `alvin-data-export-${new Date().toISOString().split('T')[0]}.json`;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      showMessage('success', 'Data exported successfully');
    } catch (error: any) {
      showMessage('error', 'Failed to export data');
    }
  };

  const deleteAccount = async () => {
    if (deleteConfirmation !== 'DELETE MY ACCOUNT') {
      showMessage('error', 'Please type "DELETE MY ACCOUNT" to confirm');
      return;
    }

    setLoading(true);
    try {
      await api.delete('/api/auth/account');
      showMessage('success', 'Account scheduled for deletion. You will be logged out.');
      setTimeout(() => logout(), 2000);
    } catch (error: any) {
      showMessage('error', error.response?.data?.message || 'Failed to delete account');
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'profile', label: 'Profile', icon: User },
    { id: 'security', label: 'Security', icon: Lock },
    { id: 'billing', label: 'Billing', icon: CreditCard },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'collaboration', label: 'Collaboration', icon: Users },
    { id: 'data', label: 'Data & Privacy', icon: Download },
    { id: 'api', label: 'API Access', icon: Key },
    { id: 'danger', label: 'Danger Zone', icon: AlertTriangle }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-7xl mx-auto py-6 px-4 sm:px-6 lg:px-8">
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-900">Settings</h1>
          <p className="mt-2 text-gray-600">Manage your account settings and preferences</p>
        </div>

        {/* Message Alert */}
        {message && (
          <div className={`mb-6 p-4 rounded-lg flex items-center justify-between ${
            message.type === 'success' 
              ? 'bg-green-50 text-green-800 border border-green-200' 
              : 'bg-red-50 text-red-800 border border-red-200'
          }`}>
            <div className="flex items-center">
              {message.type === 'success' ? (
                <CheckCircle className="w-5 h-5 mr-2" />
              ) : (
                <AlertTriangle className="w-5 h-5 mr-2" />
              )}
              {message.text}
            </div>
            <button onClick={() => setMessage(null)}>
              <X className="w-5 h-5" />
            </button>
          </div>
        )}

        <div className="bg-white shadow rounded-lg">
          <div className="border-b border-gray-200">
            <nav className="-mb-px flex space-x-8 px-6">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  className={`py-4 px-1 border-b-2 font-medium text-sm flex items-center ${
                    activeTab === tab.id
                      ? 'border-blue-500 text-blue-600'
                      : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                  }`}
                >
                  <tab.icon className="w-4 h-4 mr-2" />
                  {tab.label}
                </button>
              ))}
            </nav>
          </div>

          <div className="p-6">
            {/* Profile Tab */}
            {activeTab === 'profile' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Profile Information</h3>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Username
                      </label>
                      <input
                        type="text"
                        value={profile.username}
                        onChange={(e) => setProfile({...profile, username: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Email
                      </label>
                      <input
                        type="email"
                        value={profile.email}
                        onChange={(e) => setProfile({...profile, email: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Full Name
                      </label>
                      <input
                        type="text"
                        value={profile.full_name}
                        onChange={(e) => setProfile({...profile, full_name: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Avatar URL
                      </label>
                      <input
                        type="url"
                        value={profile.avatar_url}
                        onChange={(e) => setProfile({...profile, avatar_url: e.target.value})}
                        className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        placeholder="https://example.com/avatar.jpg"
                      />
                    </div>
                  </div>
                  <div className="mt-4">
                    <label className="block text-sm font-medium text-gray-700 mb-2">
                      Bio
                    </label>
                    <textarea
                      value={profile.bio}
                      onChange={(e) => setProfile({...profile, bio: e.target.value})}
                      rows={3}
                      className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                      placeholder="Tell us about yourself..."
                    />
                  </div>
                  <button
                    onClick={updateProfile}
                    disabled={loading}
                    className="mt-4 flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {loading ? 'Saving...' : 'Save Profile'}
                  </button>
                </div>
              </div>
            )}

            {/* Security Tab */}
            {activeTab === 'security' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Change Password</h3>
                  <div className="space-y-4 max-w-md">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Current Password
                      </label>
                      <div className="relative">
                        <input
                          type={showPasswords.current ? 'text' : 'password'}
                          value={passwordData.current_password}
                          onChange={(e) => setPasswordData({...passwordData, current_password: e.target.value})}
                          className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPasswords({...showPasswords, current: !showPasswords.current})}
                          className="absolute inset-y-0 right-0 pr-3 flex items-center"
                        >
                          {showPasswords.current ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        New Password
                      </label>
                      <div className="relative">
                        <input
                          type={showPasswords.new ? 'text' : 'password'}
                          value={passwordData.new_password}
                          onChange={(e) => setPasswordData({...passwordData, new_password: e.target.value})}
                          className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPasswords({...showPasswords, new: !showPasswords.new})}
                          className="absolute inset-y-0 right-0 pr-3 flex items-center"
                        >
                          {showPasswords.new ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-2">
                        Confirm New Password
                      </label>
                      <div className="relative">
                        <input
                          type={showPasswords.confirm ? 'text' : 'password'}
                          value={passwordData.confirm_password}
                          onChange={(e) => setPasswordData({...passwordData, confirm_password: e.target.value})}
                          className="w-full px-3 py-2 pr-10 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <button
                          type="button"
                          onClick={() => setShowPasswords({...showPasswords, confirm: !showPasswords.confirm})}
                          className="absolute inset-y-0 right-0 pr-3 flex items-center"
                        >
                          {showPasswords.confirm ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                        </button>
                      </div>
                    </div>
                    <button
                      onClick={changePassword}
                      disabled={loading || !passwordData.current_password || !passwordData.new_password}
                      className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                    >
                      <Lock className="w-4 h-4 mr-2" />
                      {loading ? 'Changing...' : 'Change Password'}
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Billing Tab */}
            {activeTab === 'billing' && billingInfo && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Billing Information</h3>
                  <div className="bg-gray-50 p-4 rounded-lg">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <p className="text-sm text-gray-600">Current Plan</p>
                        <p className="font-medium capitalize">{billingInfo.plan}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Subscription Status</p>
                        <p className="font-medium capitalize">{billingInfo.subscription_status}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Tokens Used</p>
                        <p className="font-medium">{billingInfo.tokens_used.toLocaleString()}</p>
                      </div>
                      <div>
                        <p className="text-sm text-gray-600">Tokens Remaining</p>
                        <p className="font-medium">{(billingInfo.tokens_limit - billingInfo.tokens_used).toLocaleString()}</p>
                      </div>
                    </div>
                    {billingInfo.next_billing_date && (
                      <div className="mt-4">
                        <p className="text-sm text-gray-600">Next Billing Date</p>
                        <p className="font-medium">{new Date(billingInfo.next_billing_date).toLocaleDateString()}</p>
                      </div>
                    )}
                  </div>
                  <div className="flex space-x-4 mt-4">
                    <button className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700">
                      Upgrade Plan
                    </button>
                    <button className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700">
                      Buy More Tokens
                    </button>
                  </div>
                </div>
              </div>
            )}

            {/* Notifications Tab */}
            {activeTab === 'notifications' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Notification Preferences</h3>
                  <div className="space-y-4">
                    {Object.entries(notifications).map(([key, value]) => (
                      <div key={key} className="flex items-center justify-between">
                        <div>
                          <p className="font-medium text-gray-900">
                            {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                          </p>
                          <p className="text-sm text-gray-500">
                            {key === 'email_notifications' && 'Receive email notifications for important updates'}
                            {key === 'collaboration_updates' && 'Get notified when collaborators make changes'}
                            {key === 'ai_task_completion' && 'Receive alerts when AI tasks complete'}
                            {key === 'billing_alerts' && 'Get notified about billing and payment issues'}
                            {key === 'security_alerts' && 'Receive security-related notifications'}
                          </p>
                        </div>
                        <button
                          onClick={() => setNotifications({...notifications, [key]: !value})}
                          className={`relative inline-flex h-6 w-11 items-center rounded-full transition-colors ${
                            value ? 'bg-blue-600' : 'bg-gray-200'
                          }`}
                        >
                          <span
                            className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                              value ? 'translate-x-6' : 'translate-x-1'
                            }`}
                          />
                        </button>
                      </div>
                    ))}
                  </div>
                  <button
                    onClick={updateNotifications}
                    disabled={loading}
                    className="mt-4 flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
                  >
                    <Save className="w-4 h-4 mr-2" />
                    {loading ? 'Saving...' : 'Save Preferences'}
                  </button>
                </div>
              </div>
            )}

            {/* API Tab */}
            {activeTab === 'api' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">API Access</h3>
                  <p className="text-gray-600 mb-4">
                    Create API keys to access ALVIN programmatically.
                  </p>
                  
                  <div className="flex items-center justify-between mb-4">
                    <h4 className="font-medium text-gray-900">Your API Keys</h4>
                    <button
                      onClick={() => setShowNewKeyForm(true)}
                      className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                    >
                      Create New Key
                    </button>
                  </div>

                  {showNewKeyForm && (
                    <div className="border border-gray-200 rounded-lg p-4 mb-4">
                      <h5 className="font-medium mb-2">Create New API Key</h5>
                      <div className="flex space-x-2">
                        <input
                          type="text"
                          value={newKeyName}
                          onChange={(e) => setNewKeyName(e.target.value)}
                          placeholder="API key name"
                          className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
                        />
                        <button
                          onClick={createApiKey}
                          disabled={loading}
                          className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
                        >
                          Create
                        </button>
                        <button
                          onClick={() => setShowNewKeyForm(false)}
                          className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                        >
                          Cancel
                        </button>
                      </div>
                    </div>
                  )}

                  <div className="space-y-2">
                    {apiKeys.map((key) => (
                      <div key={key.id} className="flex items-center justify-between p-3 border border-gray-200 rounded-lg">
                        <div>
                          <p className="font-medium">{key.name}</p>
                          <p className="text-sm text-gray-500">
                            Created: {new Date(key.created_at).toLocaleDateString()}
                            {key.last_used && ` • Last used: ${new Date(key.last_used).toLocaleDateString()}`}
                          </p>
                        </div>
                        <button
                          onClick={() => revokeApiKey(key.id)}
                          className="px-3 py-1 bg-red-600 text-white rounded-md hover:bg-red-700"
                        >
                          Revoke
                        </button>
                      </div>
                    ))}
                  </div>
                </div>
              </div>
            )}

            {/* Data & Privacy Tab */}
            {activeTab === 'data' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-gray-900 mb-4">Data & Privacy</h3>
                  <div className="space-y-4">
                    <div className="border border-gray-200 rounded-lg p-4">
                      <h4 className="font-medium mb-2">Export Your Data</h4>
                      <p className="text-gray-600 mb-4">
                        Download all your projects, scenes, and account data in JSON format.
                      </p>
                      <button
                        onClick={exportData}
                        className="flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                      >
                        <Download className="w-4 h-4 mr-2" />
                        Export Data
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Danger Zone Tab */}
            {activeTab === 'danger' && (
              <div className="space-y-6">
                <div>
                  <h3 className="text-lg font-medium text-red-600 mb-4">Danger Zone</h3>
                  <div className="border-2 border-red-200 rounded-lg p-4">
                    <h4 className="font-medium text-red-600 mb-2">Delete Account</h4>
                    <p className="text-gray-600 mb-4">
                      Permanently delete your account and all associated data. This action cannot be undone.
                    </p>
                    
                    {!showDeleteAccount ? (
                      <button
                        onClick={() => setShowDeleteAccount(true)}
                        className="flex items-center px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700"
                      >
                        <Trash2 className="w-4 h-4 mr-2" />
                        Delete Account
                      </button>
                    ) : (
                      <div className="space-y-4">
                        <div>
                          <label className="block text-sm font-medium text-gray-700 mb-2">
                            Type "DELETE MY ACCOUNT" to confirm
                          </label>
                          <input
                            type="text"
                            value={deleteConfirmation}
                            onChange={(e) => setDeleteConfirmation(e.target.value)}
                            className="w-full max-w-md px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-red-500"
                            placeholder="DELETE MY ACCOUNT"
                          />
                        </div>
                        <div className="flex space-x-2">
                          <button
                            onClick={deleteAccount}
                            disabled={loading || deleteConfirmation !== 'DELETE MY ACCOUNT'}
                            className="px-4 py-2 bg-red-600 text-white rounded-md hover:bg-red-700 disabled:opacity-50"
                          >
                            {loading ? 'Deleting...' : 'Confirm Delete'}
                          </button>
                          <button
                            onClick={() => {
                              setShowDeleteAccount(false);
                              setDeleteConfirmation('');
                            }}
                            className="px-4 py-2 bg-gray-300 text-gray-700 rounded-md hover:bg-gray-400"
                          >
                            Cancel
                          </button>
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Settings;