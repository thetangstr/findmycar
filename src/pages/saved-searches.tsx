import React, { useState } from 'react';
import { useRouter } from 'next/router';
import { useSavedSearches } from '@/hooks/useSavedSearches';
import Link from 'next/link';

export default function SavedSearches() {
  const router = useRouter();
  const { savedSearches, updateSavedSearch, deleteSavedSearch } = useSavedSearches();
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState('');
  
  const handleEdit = (id: string, currentName: string) => {
    setEditingId(id);
    setEditName(currentName);
  };
  
  const handleSaveEdit = (id: string) => {
    if (editName.trim()) {
      updateSavedSearch(id, { name: editName.trim() });
      setEditingId(null);
      setEditName('');
    }
  };
  
  const handleCancelEdit = () => {
    setEditingId(null);
    setEditName('');
  };
  
  const handleDelete = (id: string) => {
    if (window.confirm('Are you sure you want to delete this saved search?')) {
      deleteSavedSearch(id);
    }
  };
  
  const handleUseSearch = (id: string) => {
    const search = savedSearches.find(s => s.id === id);
    if (search) {
      router.push({
        pathname: '/search',
        query: { ...search.filters }
      });
    }
  };
  
  // Format filter values for display
  const formatFilterValue = (key: string, value: any) => {
    if (key === 'price' || key.includes('price')) {
      return `$${value.toLocaleString()}`;
    }
    if (key === 'mileage' || key.includes('mileage')) {
      return `${value.toLocaleString()} miles`;
    }
    return value;
  };
  
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Saved Searches</h1>
        <p className="text-gray-600">
          View and manage your saved search criteria for quick access.
        </p>
      </div>
      
      {savedSearches.length === 0 ? (
        <div className="bg-white rounded-lg shadow-md p-8 text-center">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 mx-auto text-gray-400 mb-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
          </svg>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">No Saved Searches</h2>
          <p className="text-gray-600 mb-6">
            You haven&apos;t saved any searches yet. When searching for vehicles, click &quot;Save Search&quot; to save your search criteria for future use.
          </p>
          <Link href="/search" className="btn btn-primary">
            Go to Search
          </Link>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {savedSearches.map(search => (
            <div key={search.id} className="bg-white rounded-lg shadow-md overflow-hidden">
              <div className="p-6">
                {editingId === search.id ? (
                  <div className="mb-4">
                    <input
                      type="text"
                      value={editName}
                      onChange={(e) => setEditName(e.target.value)}
                      className="input mb-2"
                      placeholder="Search name"
                      autoFocus
                    />
                    <div className="flex space-x-2">
                      <button
                        onClick={() => handleSaveEdit(search.id)}
                        className="btn btn-primary text-sm py-1 px-3"
                        disabled={!editName.trim()}
                      >
                        Save
                      </button>
                      <button
                        onClick={handleCancelEdit}
                        className="btn btn-secondary text-sm py-1 px-3"
                      >
                        Cancel
                      </button>
                    </div>
                  </div>
                ) : (
                  <h3 className="text-xl font-semibold text-gray-900 mb-2">
                    {search.name}
                  </h3>
                )}
                
                <div className="mb-4">
                  <h4 className="text-sm font-medium text-gray-500 mb-2">Search Criteria:</h4>
                  <div className="bg-gray-50 rounded-md p-3">
                    {Object.keys(search.filters).length === 0 ? (
                      <p className="text-gray-600 text-sm">All vehicles</p>
                    ) : (
                      <ul className="space-y-1">
                        {Object.entries(search.filters).map(([key, value]) => (
                          <li key={key} className="text-sm text-gray-700">
                            <span className="font-medium">
                              {key.replace(/([A-Z])/g, ' $1').replace(/^./, str => str.toUpperCase())}:
                            </span>{' '}
                            {formatFilterValue(key, value)}
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>
                </div>
                
                <div className="text-xs text-gray-500 mb-4">
                  Saved on {new Date(search.createdAt).toLocaleDateString()}
                </div>
                
                <div className="flex space-x-2">
                  <button
                    onClick={() => handleUseSearch(search.id)}
                    className="btn btn-primary flex-grow"
                  >
                    Use Search
                  </button>
                  <button
                    onClick={() => handleEdit(search.id, search.name)}
                    className="p-2 text-gray-600 hover:text-gray-900 bg-gray-100 hover:bg-gray-200 rounded-md"
                    title="Edit name"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z" />
                    </svg>
                  </button>
                  <button
                    onClick={() => handleDelete(search.id)}
                    className="p-2 text-red-600 hover:text-red-800 bg-red-50 hover:bg-red-100 rounded-md"
                    title="Delete search"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
