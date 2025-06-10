import { useState, useEffect, useCallback } from 'react';
import { SearchFilters } from '@/types';

interface SearchHistoryItem {
  id: string;
  filters: SearchFilters;
  timestamp: string;
}

export const useSearchHistory = () => {
  const [searchHistory, setSearchHistory] = useState<SearchHistoryItem[]>([]);
  const MAX_HISTORY_ITEMS = 10;
  
  // Load search history from localStorage on initial render
  useEffect(() => {
    const storedHistory = localStorage.getItem('searchHistory');
    if (storedHistory) {
      try {
        setSearchHistory(JSON.parse(storedHistory));
      } catch (error) {
        console.error('Failed to parse search history', error);
        localStorage.removeItem('searchHistory');
      }
    }
  }, []);
  
  // Save search history to localStorage whenever it changes
  useEffect(() => {
    localStorage.setItem('searchHistory', JSON.stringify(searchHistory));
  }, [searchHistory]);
  
  // Add a search to history
  const addToHistory = useCallback((filters: SearchFilters) => {
    // Don't add empty searches
    if (Object.keys(filters).length === 0) return;
    
    // Check if this exact search already exists
    const searchExists = searchHistory.some(item => {
      // Compare each filter property
      const itemKeys = Object.keys(item.filters);
      const filterKeys = Object.keys(filters);
      
      if (itemKeys.length !== filterKeys.length) return false;
      
      return filterKeys.every(key => {
        // @ts-ignore - We're checking for existence of dynamic keys
        return item.filters[key] === filters[key];
      });
    });
    
    if (searchExists) return;
    
    const newItem: SearchHistoryItem = {
      id: Date.now().toString(),
      filters,
      timestamp: new Date().toISOString()
    };
    
    setSearchHistory(prev => {
      // Add to beginning and limit to MAX_HISTORY_ITEMS
      return [newItem, ...prev].slice(0, MAX_HISTORY_ITEMS);
    });
  }, [searchHistory]);
  
  // Clear search history
  const clearHistory = useCallback(() => {
    setSearchHistory([]);
  }, []);
  
  return {
    searchHistory,
    addToHistory,
    clearHistory
  };
};

export default useSearchHistory;
