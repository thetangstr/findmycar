import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import { useAuth } from '@/utils/auth';
import Head from 'next/head';

/**
 * Profile Settings Page
 * 
 * Allows users to view and update their profile information
 * - Update name, email, and password
 * - View account statistics (saved searches, favorites, etc.)
 * - Delete account option
 */
export default function ProfilePage() {
  const router = useRouter();
  const { user, updateUser, logout } = useAuth();
  
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });
  
  const [isEditing, setIsEditing] = useState(false);
  const [message, setMessage] = useState({ type: '', text: '' });
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  
  // Redirect if not logged in
  useEffect(() => {
    if (!user) {
      router.push('/login?redirect=profile');
    } else {
      // Initialize form with current user data
      setFormData(prevData => ({
        ...prevData,
        name: user.name,
        email: user.email,
      }));
    }
  }, [user, router]);
  
  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value,
    }));
  };
  
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    // Validate form
    if (formData.newPassword && formData.newPassword !== formData.confirmPassword) {
      setMessage({ type: 'error', text: 'New passwords do not match' });
      return;
    }
    
    // Validate current password (in a real app, this would be verified on the server)
    if (formData.newPassword && !formData.currentPassword) {
      setMessage({ type: 'error', text: 'Current password is required to set a new password' });
      return;
    }
    
    // Update user info
    try {
      updateUser({
        name: formData.name,
        email: formData.email,
        // In a real app, password would be handled separately with proper verification
      });
      
      setMessage({ type: 'success', text: 'Profile updated successfully' });
      setIsEditing(false);
      
      // Clear password fields
      setFormData(prevData => ({
        ...prevData,
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      }));
    } catch (error) {
      setMessage({ type: 'error', text: 'Failed to update profile' });
    }
  };
  
  const handleDeleteAccount = () => {
    // In a real app, this would make an API call to delete the user's account
    logout();
    router.push('/');
  };
  
  if (!user) {
    return <div className="container mx-auto p-4">Loading...</div>;
  }
  
  return (
    <>
      <Head>
        <title>Profile Settings | FindMyCar</title>
        <meta name="description" content="Manage your FindMyCar profile settings" />
      </Head>
      
      <div className="container mx-auto p-4 max-w-4xl">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">Profile Settings</h1>
        
        {message.text && (
          <div className={`mb-4 p-3 rounded-md ${
            message.type === 'success' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'
          }`}>
            {message.text}
          </div>
        )}
        
        <div className="bg-white rounded-lg shadow-md overflow-hidden mb-8">
          <div className="p-6">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-semibold text-gray-900">Account Information</h2>
              <button
                onClick={() => setIsEditing(!isEditing)}
                className="text-primary-600 hover:text-primary-800 font-medium"
              >
                {isEditing ? 'Cancel' : 'Edit'}
              </button>
            </div>
            
            <form onSubmit={handleSubmit}>
              <div className="space-y-4">
                <div>
                  <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
                    Name
                  </label>
                  <input
                    type="text"
                    id="name"
                    name="name"
                    value={formData.name}
                    onChange={handleChange}
                    disabled={!isEditing}
                    className={`w-full p-2 border rounded-md ${
                      isEditing ? 'border-gray-300' : 'bg-gray-50 border-gray-200'
                    }`}
                    required
                  />
                </div>
                
                <div>
                  <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
                    Email
                  </label>
                  <input
                    type="email"
                    id="email"
                    name="email"
                    value={formData.email}
                    onChange={handleChange}
                    disabled={!isEditing}
                    className={`w-full p-2 border rounded-md ${
                      isEditing ? 'border-gray-300' : 'bg-gray-50 border-gray-200'
                    }`}
                    required
                  />
                </div>
                
                {isEditing && (
                  <>
                    <div className="border-t border-gray-200 pt-4 mt-4">
                      <h3 className="text-lg font-medium text-gray-900 mb-2">Change Password</h3>
                      <p className="text-sm text-gray-600 mb-4">Leave blank if you don&apos;t want to change your password</p>
                      
                      <div className="space-y-4">
                        <div>
                          <label htmlFor="currentPassword" className="block text-sm font-medium text-gray-700 mb-1">
                            Current Password
                          </label>
                          <input
                            type="password"
                            id="currentPassword"
                            name="currentPassword"
                            value={formData.currentPassword}
                            onChange={handleChange}
                            className="w-full p-2 border border-gray-300 rounded-md"
                          />
                        </div>
                        
                        <div>
                          <label htmlFor="newPassword" className="block text-sm font-medium text-gray-700 mb-1">
                            New Password
                          </label>
                          <input
                            type="password"
                            id="newPassword"
                            name="newPassword"
                            value={formData.newPassword}
                            onChange={handleChange}
                            className="w-full p-2 border border-gray-300 rounded-md"
                          />
                        </div>
                        
                        <div>
                          <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-700 mb-1">
                            Confirm New Password
                          </label>
                          <input
                            type="password"
                            id="confirmPassword"
                            name="confirmPassword"
                            value={formData.confirmPassword}
                            onChange={handleChange}
                            className="w-full p-2 border border-gray-300 rounded-md"
                          />
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex justify-end">
                      <button
                        type="submit"
                        className="btn btn-primary"
                      >
                        Save Changes
                      </button>
                    </div>
                  </>
                )}
              </div>
            </form>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md overflow-hidden mb-8">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">Account Statistics</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-gray-50 p-4 rounded-md">
                <h3 className="text-lg font-medium text-gray-900">Saved Searches</h3>
                <p className="text-3xl font-bold text-primary-600">
                  {/* This would come from an API in a real app */}
                  {localStorage.getItem('saved_searches') 
                    ? JSON.parse(localStorage.getItem('saved_searches') || '[]').length 
                    : 0}
                </p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-md">
                <h3 className="text-lg font-medium text-gray-900">Favorites</h3>
                <p className="text-3xl font-bold text-primary-600">
                  {/* This would come from an API in a real app */}
                  {localStorage.getItem('favorites') 
                    ? JSON.parse(localStorage.getItem('favorites') || '[]').length 
                    : 0}
                </p>
              </div>
              
              <div className="bg-gray-50 p-4 rounded-md">
                <h3 className="text-lg font-medium text-gray-900">Email Alerts</h3>
                <p className="text-3xl font-bold text-primary-600">
                  {/* This would come from an API in a real app */}
                  {localStorage.getItem('alerts') 
                    ? JSON.parse(localStorage.getItem('alerts') || '[]').length 
                    : 0}
                </p>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-white rounded-lg shadow-md overflow-hidden">
          <div className="p-6">
            <h2 className="text-xl font-semibold text-red-600 mb-4">Danger Zone</h2>
            
            {!showDeleteConfirm ? (
              <button
                onClick={() => setShowDeleteConfirm(true)}
                className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
              >
                Delete Account
              </button>
            ) : (
              <div className="bg-red-50 border border-red-200 rounded-md p-4">
                <p className="text-red-800 mb-4">
                  Are you sure you want to delete your account? This action cannot be undone and all your data will be permanently deleted.
                </p>
                <div className="flex space-x-4">
                  <button
                    onClick={handleDeleteAccount}
                    className="bg-red-600 text-white px-4 py-2 rounded-md hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                  >
                    Yes, Delete My Account
                  </button>
                  <button
                    onClick={() => setShowDeleteConfirm(false)}
                    className="bg-gray-200 text-gray-800 px-4 py-2 rounded-md hover:bg-gray-300 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2"
                  >
                    Cancel
                  </button>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </>
  );
}
