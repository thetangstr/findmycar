import { useState, useEffect, useCallback } from 'react';
import { SavedSearch, SearchFilters } from '@/types';

export const useSavedSearches = () => {
  const [savedSearches, setSavedSearches] = useState<SavedSearch[]>([]);

  // Load saved searches from localStorage on initial render
  useEffect(() => {
    const storedSearches = localStorage.getItem('savedSearches');
    if (storedSearches) {
      try {
        setSavedSearches(JSON.parse(storedSearches));
      } catch (error) {
        console.error('Failed to parse saved searches', error);
        localStorage.removeItem('savedSearches');
      }
    }
  }, []);

  // Save searches to localStorage whenever they change
  useEffect(() => {
    localStorage.setItem('savedSearches', JSON.stringify(savedSearches));
  }, [savedSearches]);

  // Add a new saved search
  const saveSearch = useCallback((name: string, filters: SearchFilters) => {
    const newSearch: SavedSearch = {
      id: Date.now().toString(),
      name,
      filters,
      createdAt: new Date().toISOString()
    };
    
    setSavedSearches(prev => [...prev, newSearch]);
    return newSearch;
  }, []);

  // Update an existing saved search
  const updateSavedSearch = useCallback((id: string, updates: Partial<SavedSearch>) => {
    setSavedSearches(prev => 
      prev.map(search => 
        search.id === id ? { ...search, ...updates } : search
      )
    );
  }, []);

  // Delete a saved search
  const deleteSavedSearch = useCallback((id: string) => {
    setSavedSearches(prev => prev.filter(search => search.id !== id));
  }, []);

  // Get a saved search by ID
  const getSavedSearchById = useCallback((id: string) => {
    return savedSearches.find(search => search.id === id);
  }, [savedSearches]);

  return {
    savedSearches,
    saveSearch,
    updateSavedSearch,
    deleteSavedSearch,
    getSavedSearchById
  };
};

export default useSavedSearches;
